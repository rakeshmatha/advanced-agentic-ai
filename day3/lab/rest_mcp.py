"""Day 3 IN03: REST vs MCP integration + framework bake-off.

Mirrors `Day3/IN03_API_MCP_Frameworks_Build_vs_Buy - Intro.ipynb`:

- REST: the developer hand-writes the tool schema in the agent; a manual loop
  drives the tool calls.
- MCP: the server (`day3.lab.mcp_server`) owns the schema; the client discovers
  the tools and the LLM calls them through the MCP session.
- Framework bake-off: the same store question through Python-only, LangChain, and
  LangGraph, comparing lines-of-control vs latency (a TCO decision).

    source ./activate
    restmcp                 # REST vs MCP + framework bake-off (boxed tables)
    restmcp --frameworks    # only the Python/LangChain/LangGraph comparison
    restmcp "What should we stock if it rains all week?"
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time

from typing import Annotated, TypedDict

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from common.client import build_client
from common.config import settings
from ._display import render_table
from .live_api import get_store_weather, search_demand_trends

STORE_ID = "WMT-2847"
STORE_CITY = "Bengaluru"
STORE_QUERY = (
    "Based on today's actual weather and current demand, what should we "
    f"prioritise stocking today at store {STORE_ID} in {STORE_CITY}?"
)

# --- REST approach: schema is hand-written by the developer -----------------
REST_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "store_weather",
            "description": "Get real-time weather at a Walmart India store location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"},
                    "country_code": {"type": "string"},
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "demand_trends",
            "description": "Search real-time retail demand trends and market signals.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_results": {"type": "integer"},
                },
                "required": ["query"],
            },
        },
    },
]


def _execute_rest_tool(name: str, args: dict) -> str:
    if name == "store_weather":
        return json.dumps(get_store_weather(args["city"], args.get("country_code", "IN")))
    if name == "demand_trends":
        return json.dumps(search_demand_trends(args["query"], args.get("max_results", 3)))
    return json.dumps({"error": f"unknown tool {name}"})


def rest_agent(query: str = STORE_QUERY) -> dict:
    client = build_client()
    messages = [
        {
            "role": "system",
            "content": (
                f"You are an AI assistant for Walmart India store {STORE_ID} in "
                f"{STORE_CITY}. Use tools to retrieve live data before recommending."
            ),
        },
        {"role": "user", "content": query},
    ]
    tools_called: list[str] = []
    started_at = time.time()
    for _ in range(6):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=REST_TOOLS,
            tool_choice="auto",
            temperature=0,
            max_tokens=500,
        )
        message = response.choices[0].message
        if not message.tool_calls:
            return {
                "answer": (message.content or "").strip(),
                "tools_called": tools_called,
                "latency_sec": round(time.time() - started_at, 2),
            }
        messages.append(message)
        for call in message.tool_calls:
            args = json.loads(call.function.arguments)
            result = _execute_rest_tool(call.function.name, args)
            tools_called.append(call.function.name)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
    return {
        "answer": "stopped after tool-loop limit",
        "tools_called": tools_called,
        "latency_sec": round(time.time() - started_at, 2),
    }


# --- MCP approach: client discovers the schema, LLM calls tools via session --
async def mcp_agent(query: str = STORE_QUERY) -> dict:
    params = StdioServerParameters(command=sys.executable, args=["-m", "day3.lab.mcp_server"])
    started_at = time.time()
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listed = await session.list_tools()
            discovered = [tool.name for tool in listed.tools]
            # Build OpenAI tool schema straight from the server's machine-readable schema.
            openai_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.inputSchema,
                    },
                }
                for tool in listed.tools
            ]
            client = build_client()
            messages = [
                {
                    "role": "system",
                    "content": (
                        f"You are an AI assistant for Walmart India store {STORE_ID} in "
                        f"{STORE_CITY}. Use tools to retrieve live data before recommending."
                    ),
                },
                {"role": "user", "content": query},
            ]
            tools_called: list[str] = []
            for _ in range(6):
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=openai_tools,
                    tool_choice="auto",
                    temperature=0,
                    max_tokens=500,
                )
                message = response.choices[0].message
                if not message.tool_calls:
                    return {
                        "discovered_tools": discovered,
                        "answer": (message.content or "").strip(),
                        "tools_called": tools_called,
                        "latency_sec": round(time.time() - started_at, 2),
                    }
                messages.append(message)
                for call in message.tool_calls:
                    args = json.loads(call.function.arguments)
                    result = await session.call_tool(call.function.name, args)
                    text = result.content[0].text if result.content else "{}"
                    tools_called.append(call.function.name)
                    messages.append(
                        {"role": "tool", "tool_call_id": call.id, "content": text}
                    )
            return {
                "discovered_tools": discovered,
                "answer": "stopped after tool-loop limit",
                "tools_called": tools_called,
                "latency_sec": round(time.time() - started_at, 2),
            }


# --- Framework bake-off: same question, three orchestration styles -----------
def framework_python_only(query: str) -> dict:
    """Developer pre-fetches everything, then makes one LLM call. Max control."""
    started_at = time.time()
    weather = get_store_weather(STORE_CITY)
    demand = search_demand_trends(f"retail product demand {STORE_CITY} India", max_results=2)
    client = build_client()
    response = client.chat.completions.create(
        model=settings.model,
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are an AI assistant for Walmart India store {STORE_ID} in {STORE_CITY}. "
                    f"Live weather: {json.dumps(weather)}. Demand: {demand.get('answer', '')}"
                ),
            },
            {"role": "user", "content": query},
        ],
        temperature=0,
        max_tokens=400,
    )
    return {
        "framework": "Python-only",
        "latency_sec": round(time.time() - started_at, 2),
        "data_fetch": "Manual pre-fetch (LLM cannot request more data)",
        "answer": response.choices[0].message.content.strip(),
    }


def framework_langchain(query: str) -> dict:
    """LangChain's high-level agent (v1 `create_agent`) runs the tool loop for you."""

    @tool
    def lc_weather(city: str) -> str:
        """Get real-time weather for a Walmart India store city."""
        return json.dumps(get_store_weather(city))

    @tool
    def lc_trends(query: str) -> str:
        """Search real-time retail demand trends and market signals."""
        return json.dumps(search_demand_trends(query, max_results=2))

    llm = ChatOpenAI(
        api_key=settings.openai_api_key.get_secret_value(), model=settings.model, temperature=0
    )
    agent = create_agent(
        llm,
        [lc_weather, lc_trends],
        system_prompt=(
            f"You are an AI assistant for Walmart India store {STORE_ID} in {STORE_CITY}. "
            "Use tools to retrieve live data before recommending."
        ),
    )
    started_at = time.time()
    result = agent.invoke({"messages": [HumanMessage(content=query)]})
    return {
        "framework": "LangChain",
        "latency_sec": round(time.time() - started_at, 2),
        "data_fetch": "High-level create_agent tool loop",
        "answer": result["messages"][-1].content.strip(),
    }


class _GraphState(TypedDict):
    messages: Annotated[list, add_messages]


def framework_langgraph(query: str) -> dict:
    """LangGraph with a hand-built state graph: agent <-> ToolNode loop."""

    @tool
    def lg_weather(city: str) -> str:
        """Get real-time weather for a Walmart India store city."""
        return json.dumps(get_store_weather(city))

    @tool
    def lg_trends(query: str) -> str:
        """Search real-time retail demand trends and market signals."""
        return json.dumps(search_demand_trends(query, max_results=2))

    tools = [lg_weather, lg_trends]
    llm = ChatOpenAI(
        api_key=settings.openai_api_key.get_secret_value(), model=settings.model, temperature=0
    ).bind_tools(tools)
    system = SystemMessage(
        content=(
            f"You are an AI assistant for Walmart India store {STORE_ID} in {STORE_CITY}. "
            "Use tools to retrieve live data before recommending."
        )
    )

    def agent_node(state: _GraphState) -> dict:
        return {"messages": [llm.invoke([system, *state["messages"]])]}

    def should_continue(state: _GraphState) -> str:
        return "tools" if getattr(state["messages"][-1], "tool_calls", None) else END

    graph = StateGraph(_GraphState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")
    compiled = graph.compile()

    started_at = time.time()
    result = compiled.invoke({"messages": [HumanMessage(content=query)]})
    return {
        "framework": "LangGraph",
        "latency_sec": round(time.time() - started_at, 2),
        "data_fetch": "Hand-built state graph (agent <-> ToolNode)",
        "answer": result["messages"][-1].content.strip(),
    }


def _short(text: str, width: int = 70) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= width else text[: width - 1] + "…"


def print_protocol_comparison(query: str) -> None:
    print("PROTOCOL: REST vs MCP (same question, same live APIs)")
    rest = rest_agent(query)
    mcp_result = asyncio.run(mcp_agent(query))
    print(
        render_table(
            ["Aspect", "REST", "MCP"],
            [
                ["Schema owner", "Developer writes it in the agent", "Server owns it; client discovers it"],
                ["Tool discovery", "None (hard-coded list)", f"Auto: {mcp_result['discovered_tools']}"],
                ["Tools called", ", ".join(rest["tools_called"]) or "-", ", ".join(mcp_result["tools_called"]) or "-"],
                ["Latency", f"{rest.get('latency_sec')}s", f"{mcp_result.get('latency_sec')}s"],
                ["Reuse across agents", "Copy schema into each", "Point every client at one server"],
            ],
            max_widths=[20, 34, 40],
        )
    )
    print("\nREST answer:")
    print(f"  {_short(rest['answer'], 300)}")
    print("MCP answer:")
    print(f"  {_short(mcp_result['answer'], 300)}")
    print()


def print_framework_bakeoff(query: str) -> None:
    print("FRAMEWORK BAKE-OFF: same question, three orchestration styles")
    rows = []
    for runner in (framework_python_only, framework_langchain, framework_langgraph):
        try:
            result = runner(query)
            rows.append([
                result["framework"],
                f"{result['latency_sec']}s",
                result["data_fetch"],
                _short(result["answer"], 60),
            ])
        except Exception as exc:  # noqa: BLE001 - show which framework failed, keep others
            rows.append([runner.__name__, "-", f"error: {exc}", "-"])
    print(
        render_table(
            ["Framework", "Latency", "Control flow", "Answer"],
            rows,
            max_widths=[12, 8, 30, 60],
            center={1},
        )
    )
    print(
        "\nTCO, not features: Python-only = most control/most code; LangChain = least "
        "boilerplate; LangGraph = explicit state for complex multi-step agents."
    )
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 3 IN03: REST vs MCP + framework bake-off")
    parser.add_argument("--protocol", action="store_true", help="only REST vs MCP")
    parser.add_argument("--frameworks", action="store_true", help="only the framework bake-off")
    parser.add_argument("question", nargs="*", help="store question (default: stocking query)")
    args = parser.parse_args()
    query = " ".join(args.question).strip() or STORE_QUERY

    run_protocol = args.protocol or not args.frameworks
    run_frameworks = args.frameworks or not args.protocol

    print(f"\nSTORE {STORE_ID} | {STORE_CITY}")
    print(f"QUESTION: {query}\n")
    if run_protocol:
        print_protocol_comparison(query)
    if run_frameworks:
        print_framework_bakeoff(query)


if __name__ == "__main__":
    main()
