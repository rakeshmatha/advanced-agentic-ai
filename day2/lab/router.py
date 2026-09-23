from __future__ import annotations

import sys
from time import perf_counter
from typing import Literal, NotRequired, Required, TypedDict

from day1.lab.app import settings
from day1.lab.app.workflow import answer_question
from langgraph.graph import END, START, StateGraph

from .tools import get_weather, search_web


class RouterState(TypedDict, total=False):
    question: Required[str]
    route: NotRequired[Literal["policy", "weather", "research", "escalate"]]
    answer: NotRequired[str]
    sources: NotRequired[list[str]]


class RouterUpdate(TypedDict, total=False):
    route: Literal["policy", "weather", "research", "escalate"]
    answer: str
    sources: list[str]


def classify_request(state: RouterState) -> RouterUpdate:
    question = state["question"].lower()
    if any(term in question for term in ("weather", "temperature", "forecast")):
        return {"route": "weather"}
    if any(term in question for term in ("search", "latest", "news", "research")):
        return {"route": "research"}
    action_terms = ("change", "cancel", "update", "order", "address", "status")
    route = "escalate" if any(term in question for term in action_terms) else "policy"
    return {"route": route}


def answer_policy_question(state: RouterState) -> RouterUpdate:
    answer, sources = answer_question(state["question"], settings)
    return {"answer": answer, "sources": sources}


def escalate_to_human(state: RouterState) -> RouterUpdate:
    return {
        "answer": (
            "This request needs a human support representative because the current "
            "Day 2 lab cannot perform account or order actions."
        ),
        "sources": [],
    }


def answer_weather_question(state: RouterState) -> RouterUpdate:
    question = state["question"]
    city = question.rsplit(" in ", 1)[-1].strip(" ?.\t")
    return {"answer": get_weather(city, settings), "sources": ["OpenWeatherMap"]}


def answer_research_question(state: RouterState) -> RouterUpdate:
    return {"answer": search_web(state["question"], settings), "sources": ["Tavily"]}


def build_router_graph():
    graph = StateGraph(RouterState)
    graph.add_node("classify_request", classify_request)
    graph.add_node("answer_policy_question", answer_policy_question)
    graph.add_node("answer_weather_question", answer_weather_question)
    graph.add_node("answer_research_question", answer_research_question)
    graph.add_node("escalate_to_human", escalate_to_human)
    graph.add_edge(START, "classify_request")
    graph.add_conditional_edges(
        "classify_request",
        lambda state: state["route"],
        {
            "policy": "answer_policy_question",
            "weather": "answer_weather_question",
            "research": "answer_research_question",
            "escalate": "escalate_to_human",
        },
    )
    graph.add_edge("answer_policy_question", END)
    graph.add_edge("answer_weather_question", END)
    graph.add_edge("answer_research_question", END)
    graph.add_edge("escalate_to_human", END)
    return graph.compile()


def main() -> None:
    question = " ".join(sys.argv[1:]).strip() or input("Ask a customer-service question: ")
    started_at = perf_counter()
    result = build_router_graph().invoke({"question": question})
    elapsed_seconds = perf_counter() - started_at
    print(f"\nModel: {settings.model}")
    print(f"Route: {result['route']}")
    print(f"Time taken: {elapsed_seconds:.2f} seconds\n")
    print(result["answer"])
    if result.get("sources"):
        print("\nSources:")
        for source in result["sources"]:
            print(f"- {source}")


if __name__ == "__main__":
    main()