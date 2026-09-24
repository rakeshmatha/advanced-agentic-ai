from __future__ import annotations

import sys
from time import perf_counter
from typing import Literal, NotRequired, Required, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from .llm import build_llm, run_specialist
from .tools import ORDER_TOOLS, PRODUCT_TOOLS, SERVICE_TOOLS


class RouterState(TypedDict, total=False):
    question: Required[str]
    route: NotRequired[Literal["product", "service", "order"]]
    answer: NotRequired[str]


CLASSIFIER_PROMPT = (
    "Classify the customer query into one of three categories. Reply with one word only. "
    "PRODUCT: questions about products, prices, inventory, availability, pickup. "
    "SERVICE: questions about returns, shipping, price match, store policies. "
    "ORDER: questions about order status, tracking, cancellations."
)


def classify_request(state: RouterState) -> RouterState:
    llm = build_llm(max_tokens=10)
    response = llm.invoke(
        [
            SystemMessage(content=CLASSIFIER_PROMPT),
            HumanMessage(content=state["question"]),
        ]
    )
    word = str(response.content).strip().upper()
    if "ORDER" in word:
        route: Literal["product", "service", "order"] = "order"
    elif "SERVICE" in word:
        route = "service"
    else:
        route = "product"
    return {"route": route}


def answer_product(state: RouterState) -> RouterState:
    answer = run_specialist(
        state["question"],
        build_llm(),
        PRODUCT_TOOLS,
        "You are a product specialist. Find products and check inventory.",
    )
    return {"answer": answer}


def answer_service(state: RouterState) -> RouterState:
    answer = run_specialist(
        state["question"],
        build_llm(),
        SERVICE_TOOLS,
        "You are a customer-service specialist. Handle returns, shipping, and price-match questions.",
    )
    return {"answer": answer}


def answer_order(state: RouterState) -> RouterState:
    answer = run_specialist(
        state["question"],
        build_llm(),
        ORDER_TOOLS,
        "You are an order specialist. Track orders and explain cancellation or refund policies.",
    )
    return {"answer": answer}


def route_by_intent(state: RouterState) -> Literal["product", "service", "order"]:
    route = state.get("route")
    if route == "service":
        return "service"
    if route == "order":
        return "order"
    return "product"


def build_router_graph():
    graph = StateGraph(RouterState)
    graph.add_node("classify_request", classify_request)
    graph.add_node("answer_product", answer_product)
    graph.add_node("answer_service", answer_service)
    graph.add_node("answer_order", answer_order)
    graph.add_edge(START, "classify_request")
    graph.add_conditional_edges(
        "classify_request",
        route_by_intent,
        {
            "product": "answer_product",
            "service": "answer_service",
            "order": "answer_order",
        },
    )
    graph.add_edge("answer_product", END)
    graph.add_edge("answer_service", END)
    graph.add_edge("answer_order", END)
    return graph.compile()


def run(question: str) -> RouterState:
    return build_router_graph().invoke({"question": question})


def main() -> None:
    question = " ".join(sys.argv[1:]).strip() or (
        "What is the price of milk and is it in stock?"
    )
    started_at = perf_counter()
    result = run(question)
    print(f"Route: {result.get('route')}")
    print(f"Time taken: {perf_counter() - started_at:.2f} seconds\n")
    print(result.get("answer", ""))


if __name__ == "__main__":
    main()
