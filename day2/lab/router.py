from __future__ import annotations

import sys
from typing import Literal, TypedDict

from day1.lab.application import settings
from day1.lab.application.workflow import answer_question
from langgraph.graph import END, START, StateGraph


class RouterState(TypedDict, total=False):
    question: str
    route: Literal["policy", "escalate"]
    answer: str
    sources: list[str]


def classify_request(state: RouterState) -> RouterState:
    question = state["question"].lower()
    action_terms = ("change", "cancel", "update", "order", "address", "status")
    route = "escalate" if any(term in question for term in action_terms) else "policy"
    return {"route": route}


def answer_policy_question(state: RouterState) -> RouterState:
    answer, sources = answer_question(state["question"], settings)
    return {"answer": answer, "sources": sources}


def escalate_to_human(state: RouterState) -> RouterState:
    return {
        "answer": (
            "This request needs a human support representative because the current "
            "Day 2 lab cannot perform account or order actions."
        ),
        "sources": [],
    }


def build_router_graph():
    graph = StateGraph(RouterState)
    graph.add_node("classify_request", classify_request)
    graph.add_node("answer_policy_question", answer_policy_question)
    graph.add_node("escalate_to_human", escalate_to_human)
    graph.add_edge(START, "classify_request")
    graph.add_conditional_edges(
        "classify_request",
        lambda state: state["route"],
        {"policy": "answer_policy_question", "escalate": "escalate_to_human"},
    )
    graph.add_edge("answer_policy_question", END)
    graph.add_edge("escalate_to_human", END)
    return graph.compile()


def main() -> None:
    question = " ".join(sys.argv[1:]).strip() or input("Ask a customer-service question: ")
    result = build_router_graph().invoke({"question": question})
    print(f"\nRoute: {result['route']}\n")
    print(result["answer"])
    if result.get("sources"):
        print("\nSources:")
        for source in result["sources"]:
            print(f"- {source}")


if __name__ == "__main__":
    main()