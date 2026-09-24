from __future__ import annotations

import sys
from time import perf_counter
from typing import Literal, NotRequired, Required, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from .llm import build_llm, run_specialist
from .tools import ORDER_TOOLS, PRODUCT_TOOLS, SERVICE_TOOLS

MAX_ITERATIONS = 3

SUPERVISOR_PROMPT = (
    "You are a supervisor managing a customer-support team. "
    "Given the conversation so far, decide who should respond next. "
    "Reply with one word: PRODUCT (product/inventory questions), "
    "SERVICE (returns/shipping/policy questions), "
    "ORDER (order status/tracking questions), or FINISH "
    "(the question is fully answered). If the last message is a complete, "
    "helpful answer to the customer, reply FINISH."
)


class SupervisorState(TypedDict, total=False):
    question: Required[str]
    transcript: NotRequired[str]
    next_worker: NotRequired[Literal["PRODUCT", "SERVICE", "ORDER", "FINISH"]]
    iteration: NotRequired[int]
    answer: NotRequired[str]


WorkerName = Literal["PRODUCT", "SERVICE", "ORDER", "FINISH"]


def _parse_worker(text: str) -> WorkerName:
    word = text.strip().upper()
    if "PRODUCT" in word:
        return "PRODUCT"
    if "ORDER" in word:
        return "ORDER"
    if "SERVICE" in word:
        return "SERVICE"
    return "FINISH"


def supervisor_node(state: SupervisorState) -> SupervisorState:
    iteration = state.get("iteration", 0)
    if iteration >= MAX_ITERATIONS:
        return {"next_worker": "FINISH", "iteration": iteration + 1}
    llm = build_llm(max_tokens=10)
    transcript = state.get("transcript") or f"Customer: {state['question']}"
    response = llm.invoke(
        [
            SystemMessage(content=SUPERVISOR_PROMPT),
            HumanMessage(content=transcript),
        ]
    )
    return {
        "next_worker": _parse_worker(str(response.content)),
        "iteration": iteration + 1,
        "transcript": transcript,
    }


def _append(state: SupervisorState, worker: str, answer: str) -> SupervisorState:
    transcript = state.get("transcript") or f"Customer: {state['question']}"
    updated = f"{transcript}\n{worker}: {answer}"
    return {"answer": answer, "transcript": updated}


def product_worker(state: SupervisorState) -> SupervisorState:
    answer = run_specialist(
        state["question"],
        build_llm(),
        PRODUCT_TOOLS,
        "You are a product specialist. Find products and check inventory.",
    )
    return _append(state, "PRODUCT", answer)


def service_worker(state: SupervisorState) -> SupervisorState:
    answer = run_specialist(
        state["question"],
        build_llm(),
        SERVICE_TOOLS,
        "You are a service specialist. Handle returns, shipping, and policy questions.",
    )
    return _append(state, "SERVICE", answer)


def order_worker(state: SupervisorState) -> SupervisorState:
    answer = run_specialist(
        state["question"],
        build_llm(),
        ORDER_TOOLS,
        "You are an order specialist. Track orders and explain refund policies.",
    )
    return _append(state, "ORDER", answer)


def supervisor_route(state: SupervisorState) -> WorkerName:
    return state.get("next_worker", "FINISH")


def build_supervisor_graph():
    graph = StateGraph(SupervisorState)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("product_worker", product_worker)
    graph.add_node("service_worker", service_worker)
    graph.add_node("order_worker", order_worker)
    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges(
        "supervisor",
        supervisor_route,
        {
            "PRODUCT": "product_worker",
            "SERVICE": "service_worker",
            "ORDER": "order_worker",
            "FINISH": END,
        },
    )
    graph.add_edge("product_worker", "supervisor")
    graph.add_edge("service_worker", "supervisor")
    graph.add_edge("order_worker", "supervisor")
    return graph.compile()


def run(question: str) -> SupervisorState:
    return build_supervisor_graph().invoke({"question": question, "iteration": 0})


def main() -> None:
    question = " ".join(sys.argv[1:]).strip() or (
        "Find chicken breast and tell me if I can pick it up today."
    )
    started_at = perf_counter()
    result = run(question)
    print(f"Iterations: {result.get('iteration', 0)}")
    print(f"Time taken: {perf_counter() - started_at:.2f} seconds\n")
    print(result.get("answer", ""))


if __name__ == "__main__":
    main()
