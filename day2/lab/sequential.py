from __future__ import annotations

import sys
from time import perf_counter
from typing import NotRequired, Required, TypedDict

from day1.lab.app import settings
from day1.lab.app.workflow import answer_question
from langgraph.graph import END, START, StateGraph


class SequentialState(TypedDict, total=False):
    question: Required[str]
    answer: NotRequired[str]
    sources: NotRequired[list[str]]
    elapsed_seconds: NotRequired[float]


def answer_from_policy(state: SequentialState) -> SequentialState:
    started_at = perf_counter()
    answer, sources = answer_question(state["question"], settings)
    return {
        "answer": answer,
        "sources": sources,
        "elapsed_seconds": perf_counter() - started_at,
    }


def build_sequential_graph():
    graph = StateGraph(SequentialState)
    graph.add_node("answer_from_policy", answer_from_policy)
    graph.add_edge(START, "answer_from_policy")
    graph.add_edge("answer_from_policy", END)
    return graph.compile()


def main() -> None:
    question = " ".join(sys.argv[1:]).strip() or input("Ask a customer-service question: ")
    result = build_sequential_graph().invoke({"question": question})
    print(f"\nModel: {settings.model}")
    print(f"Time taken: {result['elapsed_seconds']:.2f} seconds\n")
    print(result["answer"])
    print("\nSources:")
    for source in result.get("sources", []):
        print(f"- {source}")


if __name__ == "__main__":
    main()