"""Retail SUPERVISOR orchestration (multi-agent loop).

A LangGraph graph where a supervisor repeatedly picks the next specialist agent
(or FINISH) based on what has been gathered, then a synthesis step composes the
final answer. Best for multi-domain questions, e.g. "price of milk, is it in
stock, and can I return it?" - which touches PRODUCT, INVENTORY, and POLICY.
"""

from __future__ import annotations

from typing import Literal, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from day3.lab.llm import build_llm

from .agents import run_agent

MAX_STEPS = 6

Next = Literal["product", "inventory", "orders", "policy", "finish"]


class SupervisorDecision(BaseModel):
    """The supervisor's routing decision with brief reasoning."""

    uncovered_parts: str = Field(
        description="Which sub-questions are NOT yet answered by the findings; '' if none"
    )
    next: Literal["product", "inventory", "orders", "policy", "finish"] = Field(
        description="Next agent to call, or 'finish' only when every part is covered"
    )

SUPERVISOR_PROMPT = (
    "You are the supervisor of a Walmart retail assistant with four specialist agents:\n"
    "- PRODUCT: product details, price, SKU (needed before an inventory check)\n"
    "- INVENTORY: live stock for a SKU\n"
    "- ORDERS: order status by id\n"
    "- POLICY: returns, refunds, shipping, pickup, price match\n\n"
    "The customer question may have several parts (e.g. price AND stock AND returns). "
    "Break it into sub-questions. Choose FINISH ONLY when EVERY sub-question is already "
    "answered by the findings. If any part is still uncovered (for example a returns or "
    "policy question), pick the agent that covers it. Do not repeat an agent that already "
    "produced what you need.\n"
    "Reply with exactly one word: PRODUCT, INVENTORY, ORDERS, POLICY, or FINISH."
)

SYNTH_PROMPT = (
    "You are the Walmart assistant. Using ONLY the findings from the specialist "
    "agents, write one concise, helpful answer to the customer's question. If a "
    "detail is missing from the findings, say what is missing."
)


class SupervisorState(TypedDict, total=False):
    question: str
    findings: list[dict]  # [{"agent": str, "result": str}]
    steps: int
    next: Next
    answer: str


def _findings_text(findings: list[dict]) -> str:
    if not findings:
        return "(none yet)"
    return "\n".join(f"- {item['agent'].upper()}: {item['result']}" for item in findings)


def supervisor(state: SupervisorState) -> SupervisorState:
    findings = state.get("findings", [])
    if state.get("steps", 0) >= MAX_STEPS:
        return {"next": "finish"}
    used = [item["agent"] for item in findings]
    decider = build_llm(max_tokens=200).with_structured_output(SupervisorDecision)
    decision = decider.invoke(
        [
            SystemMessage(content=SUPERVISOR_PROMPT),
            HumanMessage(
                content=(
                    f"Customer question: {state['question']}\n\n"
                    f"Agents already used: {used or 'none'}\n"
                    f"Findings so far:\n{_findings_text(findings)}"
                )
            ),
        ]
    )
    return {"next": decision.next}


def _make_agent_node(name: str):
    def node(state: SupervisorState) -> SupervisorState:
        context = _findings_text(state.get("findings", []))
        result = run_agent(name, state["question"], context=context)
        findings = [*state.get("findings", []), {"agent": name, "result": result}]
        return {"findings": findings, "steps": state.get("steps", 0) + 1}

    return node


def synthesize(state: SupervisorState) -> SupervisorState:
    llm = build_llm(max_tokens=400)
    response = llm.invoke(
        [
            SystemMessage(content=SYNTH_PROMPT),
            HumanMessage(
                content=(
                    f"Customer question: {state['question']}\n\n"
                    f"Findings:\n{_findings_text(state.get('findings', []))}"
                )
            ),
        ]
    )
    return {"answer": str(response.content)}


def build_supervisor_graph():
    graph = StateGraph(SupervisorState)
    graph.add_node("supervisor", supervisor)
    graph.add_node("synthesize", synthesize)
    for name in ("product", "inventory", "orders", "policy"):
        graph.add_node(f"{name}_agent", _make_agent_node(name))
    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        lambda state: state["next"],
        {
            "product": "product_agent",
            "inventory": "inventory_agent",
            "orders": "orders_agent",
            "policy": "policy_agent",
            "finish": "synthesize",
        },
    )
    for name in ("product", "inventory", "orders", "policy"):
        graph.add_edge(f"{name}_agent", "supervisor")
    graph.add_edge("synthesize", END)
    return graph.compile()


def run(question: str) -> SupervisorState:
    return build_supervisor_graph().invoke(
        {"question": question, "findings": [], "steps": 0}
    )
