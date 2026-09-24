# Day 3: REST vs MCP, Agent Design, Orchestration Patterns

Status: **Complete**

Day 3 turns the Day 2 API functions into real tools and builds agents around
them. You learn how tools are exposed (**REST vs MCP**, with a real MCP server),
how to structure agents (**single vs multi-agent**), and the three
**orchestration patterns** (sequential / router / supervisor). This is where
LangGraph is used to wire agents and tools together.

## What you learn

1. **REST vs MCP (IN03)** - who owns the tool schema. REST: hand-written in each
   agent. MCP: the server owns it and clients discover tools. Includes a real
   FastMCP server (client discovers + drives a full LLM tool-loop) and a live
   **framework bake-off** (Python-only / LangChain / LangGraph on one question).
2. **Agent design (IN04)** - one agent with all tools vs a coordinator that routes
   PRODUCT vs SERVICE to specialists, and why you split.
3. **Orchestration patterns (IN05)** - sequential, router, and supervisor, and
   when each is the right shape.
4. **Retail multi-agent** - a full Walmart system that combines all of
   the above: four specialist agents (Product/Inventory/Orders/Policy), each with
   a **different** integration (REST / MCP / RAG), wrapped by LangChain and
   orchestrated by both a router (single-agent) and a supervisor (multi-agent).
   See [`retail_multi_agent/README.md`](retail_multi_agent/README.md).

## Source notebooks

- `Day3/IN03_API_MCP_Frameworks_Build_vs_Buy - Intro.ipynb`
- `Day3/IN04_Agent_Design_SingleAgent_vs_MultiAgent.ipynb`
- `Day3/IN05_Orchestration_Patterns_Sequential_Router_Supervisor.ipynb`

## Folder layout

```text
day3/
  README.md                 <- you are here
  topics/README.md          concepts: agent anatomy, REST vs MCP, orchestration
  lab/
    tools.py                shared Walmart tools (product/inventory/policy/order)
    llm.py                  shared LLM builder + specialist runner
    live_api.py             self-contained weather + demand-trends helpers
    mcp_server.py           real FastMCP server exposing store_weather/demand_trends
    rest_mcp.py             IN03: REST agent vs MCP client (auto-launches server)
    single_multi_agent.py   IN04: single agent vs coordinator + specialists
    assistant.py            interactive Walmart assistant (router) - chat
    sequential.py           IN05: classify -> tools -> quality -> format
    router.py               IN05: classify -> one specialist
    supervisor.py           IN05: supervisor <-> workers until FINISH
    compare.py              run all three patterns on shared queries (boxed table)
    _display.py             shared boxed-table helper
    README.md               per-module run guide
    deliverable/
      architecture-comparison.md   REST/MCP + agent + orchestration write-up
      README.md
  retail_multi_agent/       Walmart multi-agent system (REST+MCP+RAG)
    domains.py              4 integrations as LangChain tools + registry
    mcp_inventory_server.py FastMCP inventory server
    docs/                   policy docs for the RAG (Policy) agent
    agents.py               specialist runner over the 4 domains
    router_system.py        single-agent router (classify -> one agent)
    supervisor_system.py    multi-agent supervisor (loop -> synthesize)
    __main__.py             CLI: router / supervisor / demo / --chat
    README.md               run guide
```

## Prerequisites

- `.venv` created and dependencies installed (root `README.md`).
- `.env` keys:
  - `OPENAI_API_KEY` - required for all Day 3 labs.
  - `OPENWEATHERMAP_API_KEY`, `TAVILY_API_KEY` - used by `restmcp` / the MCP server.
- Model: `gpt-4o-mini`.
- Extra libs: `langgraph`, `langchain-openai`, and `mcp` (**pinned `<2`** because
  Day 3 uses the FastMCP API from mcp 1.x; mcp 2.x renames it).

## Setup

```bash
cd advanced-agentic-ai
source ./activate
```

## Run the homework

```bash
restmcp        # IN03: REST vs MCP (boxed) + Python/LangChain/LangGraph bake-off
singlemulti    # IN04: single-agent vs coordinator + specialists (boxed)
assistant      # interactive Walmart assistant (chat) - talk to it live
compare        # IN05: sequential vs router vs supervisor (boxed table)
retail_multi_agent  # four specialists (REST/MCP/RAG) + router and supervisor
```

Focused flags, individual patterns, and the standalone server:

```bash
restmcp --protocol            # only the REST vs MCP tables
restmcp --frameworks          # only the framework bake-off
singlemulti --chat            # talk to the multi-agent (see routing live)
assistant "Where is my order WM-2024-002?"   # one-shot
sequential "What is the price of milk and is it in stock?"
router "Check my order WM-2024-002."
supervisor "Do you price match? I saw eggs cheaper at Target."
compare --pattern router
retail_multi_agent router "How much is milk?"          # single-agent (cheapest)
retail_multi_agent supervisor "Price of milk, in stock, and can I return it?"  # multi-agent
retail_multi_agent --chat                              # interactive (supervisor)
python -m day3.lab.mcp_server     # run the MCP server on its own (stdio)
```

Equivalent: `python -m day3.lab.rest_mcp`,
`python -m day3.lab.single_multi_agent`, `python -m day3.lab.assistant`,
`python -m day3.lab.compare`.

### What each lab shows

| Lab | What happens |
| --- | --- |
| `restmcp` | REST agent (schema in code) vs an MCP client that launches `mcp_server`, **discovers** tools, and runs a full LLM tool-loop; then the same question through Python-only / LangChain / LangGraph |
| `singlemulti` | Same queries through one all-tools agent vs a coordinator that delegates to a product/service specialist, side by side |
| `assistant` | Interactive chat: classify -> route -> specialist tools -> answer |
| `compare` | Sequential, router, and supervisor on a shared query set, one boxed table with route accuracy + latency |
| `retail_multi_agent` | Four specialists (REST/MCP/RAG) under LangChain, orchestrated by a router (single) and a supervisor (multi) that hands off SKUs between agents |

## The shared tools

All Day 3 agents use the same four tools in `lab/tools.py`:
`search_product`, `check_inventory`, `get_policy`, `get_order_status`.

## Orchestration patterns at a glance

| Pattern | Control flow | Use when | Main cost |
| --- | --- | --- | --- |
| Sequential | classify -> tools -> quality -> format | Auditability, fixed steps | Most LLM calls |
| Router | classify -> one specialist | Clear, non-overlapping intents | Mis-route risk |
| Supervisor | supervisor <-> workers until FINISH | Multi-domain / retry | Medium-high latency |

## Key takeaways

- Use **REST** when one app owns a tool; adopt **MCP** when multiple hosts must
  share the same tools without copying schemas.
- Split one agent into a coordinator + specialists when tools, owners, or metrics
  diverge (context overload, skill mismatch, governance).
- **Router** is the default production shape; **supervisor** for cross-domain;
  **sequential** as the audit baseline with a quality gate.

## Deliverable

See [`lab/deliverable/architecture-comparison.md`](lab/deliverable/architecture-comparison.md)
for the REST-vs-MCP comparison, single-vs-multi-agent notes, and the orchestration
decision matrix.

## Where this leads

Days 4-5 (not yet taught) move toward evaluation/observability and production
readiness / architecture review.
