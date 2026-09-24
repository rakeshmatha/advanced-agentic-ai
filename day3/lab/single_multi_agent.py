"""Day 3: Single-agent vs multi-agent design (matches IN04).

Mirrors `Day3/IN04_Agent_Design_SingleAgent_vs_MultiAgent.ipynb`:

- Single agent: one LLM bound to all four tools, looping agent -> tools -> agent.
- Multi agent: a coordinator classifies PRODUCT vs SERVICE and delegates to a
  specialist with a smaller tool set.

    source ./activate
    singlemulti            # boxed single-vs-multi comparison on the test queries
    singlemulti --chat     # talk to the multi-agent (see routing live)
    singlemulti "Where is my order WM-2024-002?"
"""

from __future__ import annotations

import argparse
from time import perf_counter
from typing import Annotated, TypedDict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from ._display import render_table
from .llm import build_llm
from .tools import ALL_TOOLS, PRODUCT_TOOLS, SERVICE_TOOLS, TEST_QUERIES

SYSTEM_PROMPT = (
    "You are a Walmart Retail Assistant. Help customers find products, check "
    "inventory, understand store policies, and track orders. Always use the "
    "available tools to look up accurate information. Be concise and factual."
)


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def build_single_agent():
    llm = build_llm()
    llm_with_tools = llm.bind_tools(ALL_TOOLS)

    def agent_node(state: AgentState) -> dict:
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        return {"messages": [llm_with_tools.invoke(messages)]}

    def should_continue(state: AgentState) -> str:
        last = state["messages"][-1]
        if getattr(last, "tool_calls", None):
            return "tools"
        return END

    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(ALL_TOOLS))
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")
    return graph.compile()


class MultiAgentState(TypedDict):
    messages: Annotated[list, add_messages]
    route: str


COORDINATOR_PROMPT = (
    "Classify the customer query into exactly one category. Reply with only the "
    "single word PRODUCT or SERVICE. PRODUCT: products, prices, inventory, "
    "availability. SERVICE: orders, returns, shipping, or store policies."
)


def _run_specialist(state, specialist_llm, tools, system_prompt):
    messages = [SystemMessage(content=system_prompt)] + list(state["messages"])
    tool_node = ToolNode(tools)
    for _ in range(4):
        response = specialist_llm.invoke(messages)
        messages.append(response)
        if not getattr(response, "tool_calls", None):
            return {"messages": [response]}
        tool_out = tool_node.invoke({"messages": [response]})
        messages.extend(tool_out["messages"])
    return {"messages": [messages[-1]]}


def build_multi_agent():
    llm = build_llm()
    llm_product = llm.bind_tools(PRODUCT_TOOLS)
    llm_service = llm.bind_tools(SERVICE_TOOLS)

    def coordinator_node(state: MultiAgentState) -> dict:
        query = state["messages"][-1].content
        response = llm.invoke(
            [SystemMessage(content=COORDINATOR_PROMPT), HumanMessage(content=query)]
        )
        route = "product" if "PRODUCT" in str(response.content).upper() else "service"
        return {"route": route}

    def product_node(state: MultiAgentState) -> dict:
        return _run_specialist(
            state, llm_product, PRODUCT_TOOLS,
            "You are a Walmart product specialist. Find products and check inventory.",
        )

    def service_node(state: MultiAgentState) -> dict:
        return _run_specialist(
            state, llm_service, SERVICE_TOOLS,
            "You are a Walmart customer service specialist. Handle orders, returns, and policies.",
        )

    graph = StateGraph(MultiAgentState)
    graph.add_node("coordinator", coordinator_node)
    graph.add_node("product_agent", product_node)
    graph.add_node("service_agent", service_node)
    graph.set_entry_point("coordinator")
    graph.add_conditional_edges(
        "coordinator",
        lambda state: state["route"],
        {"product": "product_agent", "service": "service_agent"},
    )
    graph.add_edge("product_agent", END)
    graph.add_edge("service_agent", END)
    return graph.compile()


def _short(text: str, width: int = 60) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= width else text[: width - 1] + "…"


def run_comparison(queries: list[str]) -> None:
    single = build_single_agent()
    multi = build_multi_agent()
    rows = []
    for query in queries:
        started_at = perf_counter()
        single_state = single.invoke({"messages": [HumanMessage(content=query)]})
        single_latency = perf_counter() - started_at
        single_answer = single_state["messages"][-1].content

        started_at = perf_counter()
        multi_state = multi.invoke({"messages": [HumanMessage(content=query)], "route": ""})
        multi_latency = perf_counter() - started_at
        route = multi_state.get("route", "?").upper()
        multi_answer = multi_state["messages"][-1].content

        rows.append([
            _short(query, 38),
            f"all 4 tools\n{single_latency:.2f}s\n{_short(single_answer, 46)}",
            f"route: {route}\n{multi_latency:.2f}s\n{_short(multi_answer, 46)}",
        ])

    print("\nSINGLE-AGENT vs MULTI-AGENT (IN04)")
    print(
        render_table(
            ["Query", "Single agent", "Multi agent (coordinator + specialist)"],
            rows,
            max_widths=[38, 48, 48],
        )
    )
    print(
        "\nSingle = one LLM bound to all four tools. "
        "Multi = coordinator routes PRODUCT/SERVICE to a specialist with fewer tools."
    )


def chat_repl() -> None:
    multi = build_multi_agent()
    print("=" * 70)
    print("Day 3 Multi-agent chat (IN04)")
    print("=" * 70)
    print("Ask a Walmart question. A coordinator classifies it PRODUCT or SERVICE")
    print("and hands it to a specialist that uses only that domain's tools.")
    print("  PRODUCT tools: search_product, check_inventory")
    print("  SERVICE tools: get_policy, get_order_status")
    print()
    print("Try this:")
    print('  "What is the price of milk and is it in stock?"   -> PRODUCT')
    print('  "What is the return policy for a TV?"             -> SERVICE')
    print('  "Where is my order WM-2024-002?"                  -> SERVICE')
    print()
    print("Commands: /exit quits.")
    print("-" * 70)
    while True:
        try:
            query = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not query:
            continue
        if query == "/exit":
            break
        started_at = perf_counter()
        state = multi.invoke({"messages": [HumanMessage(content=query)], "route": ""})
        elapsed = perf_counter() - started_at
        route = state.get("route", "?").upper()
        print(f"[coordinator -> {route}]  ({elapsed:.2f}s)")
        print(f"bot> {state['messages'][-1].content}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 3 IN04 single vs multi-agent")
    parser.add_argument("--chat", action="store_true", help="talk to the multi-agent")
    parser.add_argument("query", nargs="*", help="one-shot query through both agents")
    args = parser.parse_args()
    query = " ".join(args.query).strip()

    if args.chat:
        chat_repl()
    elif query:
        run_comparison([query])
    else:
        run_comparison(TEST_QUERIES[:4])


if __name__ == "__main__":
    main()
