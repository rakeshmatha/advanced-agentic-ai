"""Day 4 guarded entry point for the real Day 3 four-agent LangGraph system.

The boundary applies request checks before graph execution, guarded read-only
REST/MCP/RAG tools, model timeouts/retries/breakers, safe supervisor findings,
moderation/output checks, privacy-safe trace/lineage events, and SLO records.
Inject ``model_factory`` and ``policy_store`` for deterministic offline tests;
production model construction uses the shared root ``.env`` OpenAI settings.
"""

from __future__ import annotations

import re
import threading
import time
import uuid
from collections import deque
from collections.abc import Callable
from contextlib import ExitStack
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import Any, Literal

from langchain_core.tools import BaseTool, StructuredTool

from .operations import (
    SlidingWindowRateLimiter,
    make_lineage_record,
    measure_slo,
    route_by_complexity,
)
from .resilience import (
    CircuitBreaker,
    CircuitOpenError,
    TransientServiceError,
    call_with_timeout,
    retry_call,
)
from .security import (
    ContentBlocked,
    has_control_characters,
    inspect_exfiltration,
    inspect_jailbreak,
    inspect_prompt,
    mask_pii,
    moderate_text,
    safe_hash,
    sanitize_untrusted_tool_output,
)

Mode = Literal["router", "supervisor"]


@dataclass(frozen=True)
class RequestPrincipal:
    """Verified identity/scope supplied by the host application, not the LLM."""

    user_id: str
    allowed_domains: frozenset[str] = frozenset({"product", "inventory", "orders", "policy"})


@dataclass
class _RequestContext:
    principal: RequestPrincipal
    request_id: str
    events: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    tool_breakers: dict[str, CircuitBreaker] = field(default_factory=dict)
    started_at: float = field(default_factory=time.monotonic)
    deadline: float = 0.0
    clock: Callable[[], float] = time.monotonic
    blocked: bool = False


_ACTIVE_REQUEST: ContextVar[_RequestContext | None] = ContextVar("day4_multi_agent_request", default=None)
_DAY3_PATCH_LOCK = threading.RLock()


class _GuardedRunnable:
    """Duck-typed LangChain model adapter with dependency timeout and breaker."""

    def __init__(
        self,
        inner: Any,
        *,
        timeout_seconds: float,
        breaker: CircuitBreaker,
    ) -> None:
        self._inner = inner
        self._timeout_seconds = timeout_seconds
        self._breaker = breaker
        self._operation_name = "model.invoke"

    def bind_tools(self, tools: list[BaseTool], **kwargs: Any) -> "_GuardedRunnable":
        wrapped = _GuardedRunnable(
            self._inner.bind_tools(tools, **kwargs),
            timeout_seconds=self._timeout_seconds,
            breaker=self._breaker,
        )
        wrapped._operation_name = self._operation_name
        return wrapped

    def with_structured_output(self, schema: Any, **kwargs: Any) -> "_GuardedStructuredRunnable":
        wrapped = _GuardedStructuredRunnable(
            self._inner.with_structured_output(schema, **kwargs),
            timeout_seconds=self._timeout_seconds,
            breaker=self._breaker,
        )
        wrapped._operation_name = self._operation_name
        return wrapped

    def invoke(self, input: Any, *args: Any, **kwargs: Any) -> Any:
        request = _ACTIVE_REQUEST.get()
        operation_name = self._operation_name
        started = time.monotonic()
        timeout_seconds = self._timeout_seconds
        if request is not None:
            timeout_seconds = min(timeout_seconds, request.deadline - request.clock())
        if timeout_seconds <= 0:
            raise TimeoutError("request deadline exceeded before model invocation")

        def invoke_once() -> Any:
            try:
                return call_with_timeout(
                    lambda: self._inner.invoke(input, *args, **kwargs),
                    timeout_seconds,
                )
            except Exception as error:
                try:
                    from openai import APIConnectionError, APITimeoutError, InternalServerError, RateLimitError
                    transient_errors = (APIConnectionError, APITimeoutError, InternalServerError, RateLimitError)
                except ImportError:
                    transient_errors = ()
                if transient_errors and isinstance(error, transient_errors):
                    raise TransientServiceError(type(error).__name__) from error
                raise

        try:
            result = self._breaker.call(
                lambda: retry_call(
                    invoke_once,
                    attempts=2,
                    base_delay_seconds=0.05,
                    max_delay_seconds=0.1,
                    retryable=(TimeoutError, TransientServiceError),
                )
            )
        except Exception as error:
            if request is not None:
                request.events.append({
                    "kind": "model", "operation": operation_name, "status": "error",
                    "error_type": type(error).__name__,
                    "latency_ms": round((time.monotonic() - started) * 1000, 3),
                })
            raise
        if request is not None:
            request.events.append({
                "kind": "model", "operation": operation_name, "status": "ok",
                "latency_ms": round((time.monotonic() - started) * 1000, 3),
            })
        return result


class _GuardedStructuredRunnable(_GuardedRunnable):
    """Structured-output counterpart; does not expose model-specific methods."""


def _tool_domains(domains: dict[str, dict[str, Any]]) -> dict[str, str]:
    return {
        tool.name: domain
        for domain, specification in domains.items()
        for tool in specification["tools"]
    }


def _answer_overlaps_evidence(answer: str, evidence: list[str]) -> bool:
    """Conservative lexical check; useful for tests, not a semantic proof."""
    if not evidence:
        return False
    ignored = {
        "status", "service", "data", "source", "sample", "training", "fixture",
        "the", "and", "with", "from", "most", "this", "that", "have", "has",
        "your", "their", "they", "into", "only", "what", "which", "within",
    }

    def terms(value: str) -> set[str]:
        return {
            word for word in re.findall(r"[a-z0-9$.-]+", value.casefold())
            if len(word) > 2 and word not in ignored
        }

    answer_terms = terms(answer)
    evidence_terms = set().union(*(terms(fact) for fact in evidence))
    overlap = answer_terms & evidence_terms
    return len(overlap) >= 2 and len(overlap) / max(1, len(answer_terms)) >= 0.35


class Day4MultiAgentHarness:
    """Run Day 3's real router/supervisor behind Day 4 request controls."""

    def __init__(
        self,
        *,
        model_factory: Callable[[int], Any] | None = None,
        moderator: Callable[[str], None] = moderate_text,
        policy_store: Any | None = None,
        request_timeout_seconds: float = 120.0,
        tool_timeout_seconds: float = 10.0,
        rate_limiter: SlidingWindowRateLimiter | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if request_timeout_seconds <= 0 or tool_timeout_seconds <= 0:
            raise ValueError("request and tool timeouts must be greater than zero")
        self.model_factory = model_factory
        self.moderator = moderator
        self.policy_store = policy_store
        self.request_timeout_seconds = request_timeout_seconds
        self.tool_timeout_seconds = tool_timeout_seconds
        self.rate_limiter = rate_limiter or SlidingWindowRateLimiter(limit=20, window_seconds=60)
        self.clock = clock
        self._model_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout_seconds=10)
        self._tool_breakers: dict[str, CircuitBreaker] = {}
        self._history: deque[dict[str, Any]] = deque(maxlen=10_000)
        self._lock = threading.Lock()
        self._model_name = "openai-configured-model" if model_factory is None else "injected-test-model"
        self._prompt_version = "day3-retail-multi-agent-guarded-v1"

    @property
    def request_history(self) -> tuple[dict[str, Any], ...]:
        """Privacy-safe request events for SLO exercises; no prompts or answers."""
        with self._lock:
            return tuple(dict(record) for record in self._history)

    def measure_slo(self, *, window_seconds: float = 300.0) -> dict[str, Any]:
        if window_seconds <= 0:
            raise ValueError("window_seconds must be greater than zero")
        cutoff = self.clock() - window_seconds
        with self._lock:
            records = [dict(record) for record in self._history if record["finished_at"] >= cutoff]
        if not records:
            raise ValueError("no multi-agent requests in the requested SLO window")
        return measure_slo(records)

    def _record_completion(self, request: _RequestContext, result: dict[str, Any], *, status: str) -> dict[str, Any]:
        elapsed_ms = round(max(0.0, (self.clock() - request.started_at) * 1000), 3)
        record = {
            "request_id": request.request_id,
            "user_hash": safe_hash(request.principal.user_id),
            "prompt_hash": safe_hash(result.pop("_prompt_for_hash", "")),
            "answer_hash": safe_hash(str(result.get("answer", ""))),
            "model_version": self._model_name,
            "prompt_version": self._prompt_version,
            "latency_sec": elapsed_ms / 1000,
            "elapsed_ms": elapsed_ms,
            "success": status in {"ok", "degraded"},
            "blocked": bool(result.get("blocked", False)),
            "status": status,
            "finished_at": self.clock(),
            "events": [dict(event) for event in request.events],
        }
        with self._lock:
            self._history.append(record)
        result["request_id"] = request.request_id
        result["lineage"] = make_lineage_record(
            request_id=request.request_id,
            user_id=request.principal.user_id,
            model_version=self._model_name,
            prompt_version=self._prompt_version,
            retrieved_context="\n".join(request.evidence),
            latency_ms=elapsed_ms,
            status=status,
        ).to_dict()
        result["trace"] = [dict(event) for event in request.events]
        return result

    def _wrap_tools(self, domains: dict[str, dict[str, Any]], request: _RequestContext) -> dict[str, list[BaseTool]]:
        by_name = _tool_domains(domains)
        wrapped: dict[str, list[BaseTool]] = {}
        for domain, specification in domains.items():
            wrapped[domain] = [self._wrap_tool(tool, domain, by_name, request) for tool in specification["tools"]]
        return wrapped

    def _wrap_tool(
        self,
        original: BaseTool,
        domain: str,
        tool_domains: dict[str, str],
        request: _RequestContext,
    ) -> BaseTool:
        def guarded_call(**arguments: Any) -> str:
            active = _ACTIVE_REQUEST.get()
            if active is None or active.request_id != request.request_id:
                raise PermissionError("tool call has no active authenticated request context")
            if domain not in active.principal.allowed_domains:
                active.events.append({
                    "kind": "tool", "tool": original.name, "domain": domain,
                    "status": "denied", "latency_ms": 0.0,
                })
                raise PermissionError(f"principal is not authorized for domain {domain}")

            started = self.clock()
            breaker = active.tool_breakers.setdefault(
                original.name,
                self._tool_breakers.setdefault(
                    original.name,
                    CircuitBreaker(failure_threshold=2, recovery_timeout_seconds=8),
                ),
            )

            def invoke_read_only_tool() -> str:
                try:
                    remaining = request.deadline - self.clock()
                    if remaining <= 0:
                        raise TimeoutError("request deadline exceeded before tool invocation")
                    value = call_with_timeout(
                        lambda: original.invoke({
                            key: mask_pii(value) if isinstance(value, str) else value
                            for key, value in arguments.items()
                        }),
                        min(self.tool_timeout_seconds, remaining),
                    )
                except Exception as error:
                    if isinstance(error, PermissionError):
                        raise
                    raise TransientServiceError(type(error).__name__) from error
                return str(value)

            try:
                raw_output = breaker.call(
                    lambda: retry_call(
                        invoke_read_only_tool,
                        attempts=2,
                        base_delay_seconds=0.03,
                        max_delay_seconds=0.08,
                        retryable=(TransientServiceError,),
                    )
                )
                safe_output = mask_pii(raw_output)
                request.evidence.append(safe_output)
                safe_output = sanitize_untrusted_tool_output(safe_output)
                status = "ok"
            except Exception as error:
                safe_output = f"DEPENDENCY_UNAVAILABLE: {original.name}; do not infer a result; escalate or retry later."
                status = "degraded"
                request.events.append({
                    "kind": "tool", "tool": original.name, "domain": domain,
                    "status": status, "error_type": type(error).__name__,
                    "latency_ms": round((self.clock() - started) * 1000, 3),
                })
            if status == "ok":
                request.events.append({
                    "kind": "tool", "tool": original.name, "domain": domain,
                    "status": status, "latency_ms": round((self.clock() - started) * 1000, 3),
                    "argument_hash": safe_hash(repr(sorted(arguments.items()))),
                })
            return safe_output

        return StructuredTool.from_function(
            func=guarded_call,
            name=original.name,
            description=original.description or f"Guarded read-only {domain} lookup",
            args_schema=original.args_schema,
        )

    def _build_live_model(self, max_tokens: int) -> Any:
        from common.config import settings
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            api_key=settings.openai_api_key.get_secret_value(),
            model=settings.model,
            temperature=0,
            max_tokens=max_tokens,
            timeout=min(self.request_timeout_seconds, 35.0),
            max_retries=0,
        )

    def _new_model(self, max_tokens: int = 500) -> _GuardedRunnable:
        inner = self.model_factory(max_tokens) if self.model_factory is not None else self._build_live_model(max_tokens)
        model = _GuardedRunnable(
            inner,
            timeout_seconds=min(self.request_timeout_seconds, 35.0),
            breaker=self._model_breaker,
        )
        model._operation_name = {
            5: "router.classify",
            200: "supervisor.decide",
            400: "supervisor.synthesize",
        }.get(max_tokens, "specialist.invoke")
        return model

    def run(
        self,
        question: str,
        *,
        principal: RequestPrincipal,
        mode: Mode = "supervisor",
    ) -> dict[str, Any]:
        """Validate a request and execute the real Day 3 LangGraph router/supervisor."""
        started_at = self.clock()
        request = _RequestContext(
            principal=principal,
            request_id=uuid.uuid4().hex,
            started_at=started_at,
            deadline=started_at + self.request_timeout_seconds,
            clock=self.clock,
        )
        raw_question = question if isinstance(question, str) else ""

        def finish(answer: str, *, status: str, reason: str, blocked: bool) -> dict[str, Any]:
            result: dict[str, Any] = {
                "answer": mask_pii(answer),
                "status": status,
                "reason": reason,
                "blocked": blocked,
                "mode": mode,
                "route": None,
                "findings": [],
                "_prompt_for_hash": raw_question,
            }
            request.blocked = blocked
            return self._record_completion(request, result, status=status)

        if mode not in {"router", "supervisor"}:
            return finish("Unsupported orchestration mode.", status="blocked", reason="invalid_mode", blocked=True)
        if not principal.user_id:
            return finish("A verified user identity is required.", status="blocked", reason="missing_identity", blocked=True)
        if not isinstance(question, str) or not question.strip():
            return finish("The request is empty or invalid.", status="blocked", reason="input_validation", blocked=True)
        if len(question) > 2_000 or has_control_characters(question):
            return finish("The request is invalid or too long.", status="blocked", reason="input_validation", blocked=True)
        if inspect_prompt(question).blocked or inspect_jailbreak(question).blocked:
            return finish("I cannot follow instruction-override requests.", status="blocked", reason="injection_detected", blocked=True)
        if inspect_exfiltration(question).blocked:
            return finish("I cannot provide private or internal data.", status="blocked", reason="exfiltration_request", blocked=True)

        rate = self.rate_limiter.check(principal.user_id)
        if not rate.allowed:
            response = finish("Request limit reached. Please retry shortly.", status="blocked", reason="rate_limited", blocked=True)
            response["retry_after_seconds"] = rate.retry_after_seconds
            return response

        safe_question = mask_pii(question)
        try:
            self.moderator(safe_question)
        except ContentBlocked:
            return finish("I cannot help with that request.", status="blocked", reason="input_moderation", blocked=True)
        except Exception:
            return finish("Safety checks are temporarily unavailable.", status="blocked", reason="moderation_unavailable", blocked=True)

        try:
            from day3.retail_multi_agent import domains, router_system, supervisor_system
            from day3.retail_multi_agent.agents import (
                AGENT_FINDING_GUARD,
                AGENT_TOOL_OVERRIDES,
            )

            tools = self._wrap_tools(domains.DOMAINS, request)
            with _DAY3_PATCH_LOCK, ExitStack() as stack:
                if self.policy_store is not None:
                    previous_vector_store = domains._VECTOR_STORE
                    previous_policy_store = domains._policy_store
                    stack.callback(setattr, domains, "_VECTOR_STORE", previous_vector_store)
                    stack.callback(setattr, domains, "_policy_store", previous_policy_store)
                    domains._VECTOR_STORE = None
                    domains._policy_store = lambda: self.policy_store

                # Each test/live factory still feeds the real graph, agents,
                # specialist tool loop, and LangGraph ToolNode execution path.
                from day3.retail_multi_agent import agents
                factory = self.model_factory or self._new_model
                for module in (router_system, supervisor_system, agents):
                    previous_factory = module.build_llm
                    stack.callback(setattr, module, "build_llm", previous_factory)
                    module.build_llm = factory

                def guard_finding(text: str) -> str:
                    safe_text = mask_pii(text)
                    try:
                        self.moderator(safe_text)
                    except Exception as error:
                        request.events.append({
                            "kind": "specialist_output_guard", "status": "blocked",
                            "error_type": type(error).__name__,
                        })
                        return "SPECIALIST_FINDING_BLOCKED: safety review is required."
                    if inspect_prompt(safe_text).blocked or inspect_exfiltration(safe_text).blocked:
                        request.events.append({
                            "kind": "specialist_output_guard", "status": "blocked",
                            "reason": "untrusted_instruction_or_exfiltration_marker",
                        })
                        return "SPECIALIST_FINDING_BLOCKED: safety review is required."
                    return sanitize_untrusted_tool_output(safe_text)

                tool_token: Token[dict[str, list[BaseTool]] | None] = AGENT_TOOL_OVERRIDES.set(tools)
                finding_token: Token[Callable[[str], str] | None] = AGENT_FINDING_GUARD.set(guard_finding)
                request_token: Token[_RequestContext | None] = _ACTIVE_REQUEST.set(request)
                stack.callback(_ACTIVE_REQUEST.reset, request_token)
                stack.callback(AGENT_FINDING_GUARD.reset, finding_token)
                stack.callback(AGENT_TOOL_OVERRIDES.reset, tool_token)

                if mode == "router":
                    graph = router_system.build_router_graph()
                    graph_result = graph.invoke({"question": safe_question})
                else:
                    graph = supervisor_system.build_supervisor_graph()
                    graph_result = graph.invoke(
                        {"question": safe_question, "findings": [], "steps": 0}
                    )

            answer = mask_pii(str(graph_result.get("answer", "")))
            if not answer.strip():
                return finish("The assistant could not produce a verified response.", status="degraded", reason="empty_answer", blocked=False)
            try:
                self.moderator(answer)
            except Exception:
                return finish("The response could not be cleared by the safety service.", status="blocked", reason="output_moderation", blocked=True)
            if inspect_exfiltration(answer).blocked:
                return finish("The response was blocked by a safety check.", status="blocked", reason="output_exfiltration_guard", blocked=True)
            if not _answer_overlaps_evidence(answer, request.evidence):
                return finish(
                    "I could not verify that response against the approved tool results. Please try again or contact support.",
                    status="degraded", reason="grounding_not_verified", blocked=False,
                )

            status = "degraded" if any(event.get("status") in {"degraded", "error"} for event in request.events) else "ok"
            result = {
                "answer": answer,
                "status": status,
                "reason": "dependency_fallback" if status == "degraded" else "",
                "blocked": False,
                "mode": mode,
                "route": graph_result.get("route"),
                "findings": graph_result.get("findings", []),
                "_prompt_for_hash": raw_question,
            }
            return self._record_completion(request, result, status=status)
        except Exception as error:
            request.events.append({
                "kind": "orchestrator", "status": "error", "error_type": type(error).__name__,
                "latency_ms": round((self.clock() - started_at) * 1000, 3),
            })
            return finish(
                "The assistant is temporarily unavailable. Please try again later.",
                status="degraded", reason=f"orchestration_{type(error).__name__}", blocked=False,
            )
