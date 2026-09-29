"""Retail specialist agents: run one domain agent on a question.

Each agent is the shared LLM specialised with a domain system prompt and that
domain's tool(s). Reuses the Day 3 specialist runner.
"""

from __future__ import annotations

from collections.abc import Callable
from contextvars import ContextVar

from langchain_core.tools import BaseTool

from day3.lab.llm import build_llm, run_specialist

from .domains import DOMAINS

AGENT_TOOL_OVERRIDES: ContextVar[dict[str, list[BaseTool]] | None] = ContextVar(
    "agent_tool_overrides", default=None
)
AGENT_FINDING_GUARD: ContextVar[Callable[[str], str] | None] = ContextVar(
    "agent_finding_guard", default=None
)


def run_agent(name: str, question: str, context: str = "") -> str:
    """Run the named specialist agent, optionally with context from other agents."""
    spec = DOMAINS[name]
    overrides = AGENT_TOOL_OVERRIDES.get()
    tools = overrides.get(name, spec["tools"]) if overrides is not None else spec["tools"]
    prompt = spec["prompt"]
    user_input = question
    if context:
        user_input = f"{question}\n\nContext gathered from other agents:\n{context}"
    return run_specialist(user_input, build_llm(), tools, prompt)
