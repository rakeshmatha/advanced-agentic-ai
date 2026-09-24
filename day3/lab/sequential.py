from __future__ import annotations

import sys
from time import perf_counter
from typing import NotRequired, Required, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from .llm import build_llm
from .tools import ALL_TOOLS


class SequentialState(TypedDict, total=False):
    question: Required[str]
    intent: NotRequired[str]
    tool_output: NotRequired[str]
    quality_ok: NotRequired[bool]
    answer: NotRequired[str]


def classify_intent(state: SequentialState) -> SequentialState:
    llm = build_llm(max_tokens=40)
    response = llm.invoke(
        [
            SystemMessage(
                content=(
                    "Classify this customer query in 3 words or fewer: "
                    "PRODUCT_LOOKUP, ORDER_STATUS, RETURN_POLICY, PRICE_MATCH, "
                    "PICKUP_INFO, or OTHER."
                )
            ),
            HumanMessage(content=state["question"]),
        ]
    )
    return {"intent": str(response.content).strip()}


def execute_tools(state: SequentialState) -> SequentialState:
    llm = build_llm()
    bound = llm.bind_tools(ALL_TOOLS)
    messages = [
        SystemMessage(
            content="You are a customer-service assistant. Use tools to answer accurately."
        ),
        HumanMessage(content=state["question"]),
    ]
    response = bound.invoke(messages)
    tool_calls = getattr(response, "tool_calls", None)
    if tool_calls:
        tool_out = ToolNode(ALL_TOOLS).invoke({"messages": [response]})
        tool_text = " | ".join(
            str(message.content)
            for message in tool_out["messages"]
            if hasattr(message, "content")
        )
        final = llm.invoke(messages + [response] + tool_out["messages"])
        return {"tool_output": tool_text, "answer": str(final.content)}
    return {"tool_output": str(response.content), "answer": str(response.content)}


def quality_check(state: SequentialState) -> SequentialState:
    llm = build_llm(max_tokens=10)
    check = llm.invoke(
        [
            SystemMessage(
                content="Does this response directly answer the customer query? Reply YES or NO only."
            ),
            HumanMessage(
                content=f"Query: {state['question']}\nResponse: {state.get('answer', '')}"
            ),
        ]
    )
    return {"quality_ok": "YES" in str(check.content).upper()}


def format_response(state: SequentialState) -> SequentialState:
    if state.get("quality_ok", True):
        return {"answer": state.get("answer", "")}
    fallback = (
        "I was unable to find a complete answer. Please contact a human support representative."
    )
    return {"answer": fallback}


def build_sequential_graph():
    graph = StateGraph(SequentialState)
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("execute_tools", execute_tools)
    graph.add_node("quality_check", quality_check)
    graph.add_node("format_response", format_response)
    graph.add_edge(START, "classify_intent")
    graph.add_edge("classify_intent", "execute_tools")
    graph.add_edge("execute_tools", "quality_check")
    graph.add_edge("quality_check", "format_response")
    graph.add_edge("format_response", END)
    return graph.compile()


def run(question: str) -> SequentialState:
    return build_sequential_graph().invoke({"question": question})


def main() -> None:
    question = " ".join(sys.argv[1:]).strip() or (
        "What is the price of milk and is it in stock?"
    )
    started_at = perf_counter()
    result = run(question)
    print(f"Intent: {result.get('intent')}")
    print(f"Quality: {'PASS' if result.get('quality_ok') else 'FAIL'}")
    print(f"Time taken: {perf_counter() - started_at:.2f} seconds\n")
    print(result.get("answer", ""))


if __name__ == "__main__":
    main()
