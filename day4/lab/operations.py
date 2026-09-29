"""Governance and operations exercises for Day 4 (IN09), all offline."""

from __future__ import annotations

import math
import threading
import time
from collections import deque
from collections.abc import Callable, Iterable, Iterator
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

from .security import safe_hash

SLO_TARGETS: dict[str, float] = {
    "p50_latency_ms": 800.0,
    "p95_latency_ms": 2_000.0,
    "p99_latency_ms": 4_000.0,
    "availability_pct": 99.9,
    "block_rate_pct": 1.0,
}


@dataclass(frozen=True)
class LineageRecord:
    """Minimal, privacy-conscious provenance record; raw prompts are omitted."""

    request_id: str
    user_hash: str
    model_version: str
    prompt_version: str
    context_hash: str
    latency_ms: float
    status: str
    timestamp_utc: str

    def to_dict(self) -> dict[str, str | float]:
        return asdict(self)


def make_lineage_record(
    *,
    request_id: str,
    user_id: str,
    model_version: str,
    prompt_version: str,
    retrieved_context: str,
    latency_ms: float,
    status: str,
) -> LineageRecord:
    if latency_ms < 0 or not math.isfinite(latency_ms):
        raise ValueError("latency_ms must be finite and non-negative")
    return LineageRecord(
        request_id=request_id,
        user_hash=safe_hash(user_id),
        model_version=model_version,
        prompt_version=prompt_version,
        context_hash=safe_hash(retrieved_context),
        latency_ms=round(latency_ms, 3),
        status=status,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
    )


def route_by_complexity(query: str) -> str:
    """Route obvious multi-part/high-reasoning queries to the complex path."""
    normalized = query.casefold()
    indicators = ("compare", "and then", "why", "because", "step by step", "summarize")
    question_count = normalized.count("?")
    if len(normalized) > 180 or question_count > 1 or any(token in normalized for token in indicators):
        return "complex"
    return "simple"


def stream_chunks(text: str, *, chunk_size: int = 16) -> Iterator[str]:
    """Yield response chunks for a local streaming demonstration."""
    if chunk_size < 1:
        raise ValueError("chunk_size must be at least one")
    for start in range(0, len(text), chunk_size):
        yield text[start : start + chunk_size]


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    calls_in_window: int
    retry_after_seconds: float


class SlidingWindowRateLimiter:
    """Thread-safe in-memory per-key sliding-window limiter.

    This is process-local classroom code, not a distributed production limiter.
    """

    def __init__(
        self,
        *,
        limit: int = 20,
        window_seconds: float = 60.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if limit < 1:
            raise ValueError("limit must be at least one")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be greater than zero")
        self.limit = limit
        self.window_seconds = window_seconds
        self._clock = clock
        self._requests: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def check(self, key: str) -> RateLimitDecision:
        if not key:
            raise ValueError("rate-limit key must not be empty")
        now = self._clock()
        cutoff = now - self.window_seconds
        with self._lock:
            calls = self._requests.setdefault(key, deque())
            while calls and calls[0] <= cutoff:
                calls.popleft()
            if len(calls) >= self.limit:
                retry_after = max(0.0, self.window_seconds - (now - calls[0]))
                return RateLimitDecision(False, len(calls), round(retry_after, 3))
            calls.append(now)
            return RateLimitDecision(True, len(calls), 0.0)


def fallback_chain(
    query: str,
    *,
    primary: Callable[[], str],
    secondary: Callable[[], str],
    cache_lookup: Callable[[str], str | None],
    graceful_default: str,
) -> dict[str, object]:
    """Try primary, secondary, cache, and safe default in that order."""
    trace: list[str] = []
    for source, operation in (("primary", primary), ("secondary", secondary)):
        try:
            answer = operation()
            if not answer.strip():
                raise ValueError("empty model response")
        except Exception as error:
            trace.append(f"{source}: FAILED ({type(error).__name__})")
            continue
        trace.append(f"{source}: SUCCESS")
        return {"answer": answer, "source": source, "trace": trace}

    try:
        cached = cache_lookup(query)
    except Exception as error:
        trace.append(f"cache: FAILED ({type(error).__name__})")
        cached = None
    if cached:
        trace.append("cache: HIT")
        return {"answer": cached, "source": "cache", "trace": trace}
    trace.append("cache: MISS")
    trace.append("graceful_default: USED")
    return {"answer": graceful_default, "source": "graceful_default", "trace": trace}


def _nearest_rank(values: list[float], percentile: float) -> float:
    rank = max(1, math.ceil(percentile / 100 * len(values)))
    return values[rank - 1]


def measure_slo(
    call_records: Iterable[dict[str, object]],
    *,
    targets: dict[str, float] | None = None,
) -> dict[str, object]:
    """Measure latency percentiles, availability, and block rate.

    Percentiles use the nearest-rank method. A blocked request is measured
    separately from availability, matching the instructor notebook's schema.
    """
    records = list(call_records)
    if not records:
        raise ValueError("at least one call record is required")

    latencies: list[float] = []
    for record in records:
        raw_latency = record.get("latency_sec")
        if not isinstance(raw_latency, (int, float)) or not math.isfinite(raw_latency) or raw_latency < 0:
            raise ValueError("every latency_sec must be finite and non-negative")
        latencies.append(float(raw_latency) * 1000)

    success_count = sum(bool(record.get("success", True)) for record in records)
    blocked_count = sum(bool(record.get("blocked", False)) for record in records)
    latencies.sort()
    measurements: dict[str, object] = {
        "total_calls": len(records),
        "p50_latency_ms": round(_nearest_rank(latencies, 50), 1),
        "p95_latency_ms": round(_nearest_rank(latencies, 95), 1),
        "p99_latency_ms": round(_nearest_rank(latencies, 99), 1),
        "availability_pct": round(success_count / len(records) * 100, 3),
        "block_rate_pct": round(blocked_count / len(records) * 100, 3),
        "percentile_method": "nearest-rank",
        "measurement_scope": "synthetic training data unless sourced otherwise",
    }

    active_targets = targets or SLO_TARGETS
    compliance: dict[str, dict[str, object]] = {}
    for metric, target in active_targets.items():
        measured = measurements[metric]
        passed = measured >= target if metric == "availability_pct" else measured <= target # type: ignore
        compliance[metric] = {
            "target": target,
            "measured": measured,
            "status": "OK" if passed else "BREACH",
        }
    measurements["slo_violations"] = compliance
    return measurements
