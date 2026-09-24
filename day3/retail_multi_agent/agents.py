"""Retail specialist agents: run one domain agent on a question.

Each agent is the shared LLM specialised with a domain system prompt and that
domain's tool(s). Reuses the Day 3 specialist runner.
"""

from __future__ import annotations

from day3.lab.llm import build_llm, run_specialist

from .domains import DOMAINS


def run_agent(name: str, question: str, context: str = "") -> str:
    """Run the named specialist agent, optionally with context from other agents."""
    spec = DOMAINS[name]
    prompt = spec["prompt"]
    user_input = question
    if context:
        user_input = f"{question}\n\nContext gathered from other agents:\n{context}"
    return run_specialist(user_input, build_llm(), spec["tools"], prompt)
