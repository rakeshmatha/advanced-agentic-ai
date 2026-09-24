# Day 3 `retail_multi_agent` — Walmart multi-agent system

Puts Day 3 together in one runnable system: four specialist agents, each using a
**different integration style**, wrapped as LangChain tools, and coordinated by
**two LangGraph orchestrators** — a single-agent **router** and a multi-agent
**supervisor**. Python is the glue.

## The idea

A retailer like Walmart doesn't build one giant agent. It builds focused
specialists that each talk to a different backend, then an orchestrator decides
who to call:

| Agent     | Integration | Tool              | Backend                                   |
| --------- | ----------- | ----------------- | ----------------------------------------- |
| Product   | **REST**    | `product_search`  | internal Product Service (price/aisle/SKU)|
| Inventory | **MCP**     | `inventory_check` | Inventory MCP server (live stock by SKU)  |
| Orders    | **REST**    | `order_status`    | internal Orders Service (status by id)    |
| Policy    | **RAG**     | `policy_lookup`   | FAISS over `docs/` (returns/shipping)     |

## Two orchestrators

**Router (single-agent).** Classifies the question and hands it to exactly ONE
agent. Lowest cost, lowest latency — best when a question lives in a single
domain (e.g. *"What is the return policy for a TV?"* → POLICY).

```
question -> classify -> [product | inventory | orders | policy] -> answer
```

**Supervisor (multi-agent).** Loops across agents until every part of the
question is covered, then synthesizes one answer. Best for multi-part
questions that cross domains (e.g. *"What's the price of milk, is it in stock,
and can I return it?"* → PRODUCT → INVENTORY → POLICY).

```
question -> supervisor -> agent -> supervisor -> ... -> FINISH -> synthesize
```

The supervisor decides each step with a structured-output LLM call
(`SupervisorDecision`) that names which sub-questions are still uncovered, so it
keeps going until price, stock, and returns are all answered instead of
stopping early. A `MAX_STEPS` guard prevents runaway loops.

Notice the **PRODUCT → INVENTORY handoff**: PRODUCT returns the SKU, which the
supervisor passes as context so INVENTORY can check stock by SKU (MCP).

## How to run

```bash
source ./activate

retail_multi_agent                          # demo: router (single) + supervisor (multi)

# Router — single-domain, cheapest
retail_multi_agent router "How much is milk?"
retail_multi_agent router "What is the status of order WM-2024-002?"
retail_multi_agent router "Is Great Value whole milk in stock?"
retail_multi_agent router "What is the return policy for a TV?"

# Supervisor — multi-domain, agents cooperate
retail_multi_agent supervisor "What is the price of milk, is it in stock, and can I return it if unopened?"

# Interactive
retail_multi_agent --chat                   # supervisor by default
retail_multi_agent --chat --mode router     # router
```

Without the alias: `python -m day3.retail_multi_agent [router|supervisor|demo] "..."`.

## Files

| File                       | Role                                                        |
| -------------------------- | ----------------------------------------------------------- |
| `domains.py`               | The 4 integrations as LangChain `@tool`s + the `DOMAINS` registry |
| `mcp_inventory_server.py`  | FastMCP server exposing `check_inventory` / `low_stock`     |
| `docs/`                    | Policy markdown used by the RAG (Policy) agent              |
| `agents.py`                | Runs one specialist over its domain's tools + prompt        |
| `router_system.py`         | LangGraph single-agent router (classify → one agent)        |
| `supervisor_system.py`     | LangGraph multi-agent supervisor (loop → synthesize)        |
| `__main__.py`              | CLI: `router` / `supervisor` / `demo` / `--chat`            |

## Sample data

Products: `milk`, `bread`, `eggs`, `butter`, `chicken`
(SKUs like `GV-MILK-1G`). Orders: `WM-2024-001` … `WM-2024-004`.
Policies: returns/refunds and shipping/price-match in `docs/`.

## What this demonstrates (Day 3 concepts)

- **REST vs MCP vs RAG** integration styles, side by side, in one system.
- **LangChain** as the agent/tool framework; **Python** as the glue.
- **LangGraph** orchestration in two flavors: a **router** (single agent) and a
  **supervisor** (multi-agent with a synthesis step).
- **Single vs multi-agent** trade-offs: the router is cheaper/faster for
  single-domain questions; the supervisor is needed when a question spans
  domains and requires an inter-agent handoff.
