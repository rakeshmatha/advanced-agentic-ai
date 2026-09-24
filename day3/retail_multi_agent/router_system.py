"""Retail ROUTER orchestration (single-agent per query).

A LangGraph graph: classify the question into one domain, then run that single
specialist agent. Best for clear, single-domain questions (lowest cost).
"""

from __future__ import annotations

from typing import Literal, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph

from day3.lab.llm import build_llm

from .agents import run_agent

Route = Literal["product", "inventory", "orders", "policy"]

CLASSIFIER_PROMPT = (
    "Classify the customer query into exactly one domain. Reply with one word only.\n"
    "PRODUCT: product details, price, aisle, SKU.\n"
    "INVENTORY: whether an item is in stock, stock levels.\n"
    "ORDERS: order status, tracking, cancellation by order id.\n"
    "POLICY: returns, refunds, shipping, pickup, price match."
)


class RouterState(TypedDict, total=False):
    question: str
    route: Route
    answer: str


def classify(state: RouterState) -> RouterState:
    llm = build_llm(max_tokens=5)
    response = llm.invoke(
        [SystemMessage(content=CLASSIFIER_PROMPT), HumanMessage(content=state["question"])]
    )
    word = str(response.content).strip().upper()
    if "INVENTORY" in word:
        route: Route = "inventory"
    elif "ORDER" in word:
        route = "orders"
    elif "POLICY" in word:
        route = "policy"
    else:
        route = "product"
    return {"route": route}


def _make_agent_node(name: Route):
    def node(state: RouterState) -> RouterState:
        return {"answer": run_agent(name, state["question"])}

    return node


def build_router_graph():
    graph = StateGraph(RouterState)
    graph.add_node("classify", classify)
    for name in ("product", "inventory", "orders", "policy"):
        graph.add_node(f"{name}_agent", _make_agent_node(name))  # type: ignore[arg-type]
    graph.add_edge(START, "classify")
    graph.add_conditional_edges(
        "classify",
        lambda state: state["route"],
        {
            "product": "product_agent",
            "inventory": "inventory_agent",
            "orders": "orders_agent",
            "policy": "policy_agent",
        },
    )
    for name in ("product", "inventory", "orders", "policy"):
        graph.add_edge(f"{name}_agent", END)
    return graph.compile()


def run(question: str) -> RouterState:
    return build_router_graph().invoke({"question": question})
