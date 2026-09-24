# Day 3 Topics: Protocols, Agent Design, Orchestration

What the instructor taught on Day 3. Builds on Day 2 tools and RAG.

## 1. REST vs MCP (IN03)

- **REST**: the developer writes the tool schema inside each agent. Mature and
  easy to monitor, but the schema is copied into every agent that needs it.
- **MCP**: the server owns the schema; any client discovers and calls tools with
  no hand-written descriptions. Better when many hosts share one tool catalog.

Framework selection is a total-cost-of-ownership choice: Python-only (max
control), LangChain (reusable integrations), LangGraph (explicit state).

Runnable: `python -m day3.lab.rest_mcp` (launches a real FastMCP server)

## 2. Agent Anatomy: single vs multi (IN04)

An agent = planning + memory + state + tool calling + action. One agent with all
tools works at small scale, but breaks down through context overload, skill
mismatch, no parallelism, a single failure domain, and governance leaks. Split
into a coordinator + specialists when tools, owners, or metrics diverge.

Runnable: `python -m day3.lab.single_multi_agent`

## 3. Orchestration Patterns (IN05)

| Pattern | Control flow | When to use | Main cost |
| --- | --- | --- | --- |
| Sequential | classify → tools → quality → format | Auditability, fixed steps | Highest LLM-call count |
| Router | classify → one specialist | Clear, non-overlapping intents | Mis-route risk |
| Supervisor | supervisor ↔ workers until FINISH | Multi-domain or retry | Medium-high latency |

Runnable: `python -m day3.lab.compare`

## Failure modes to watch

Timeout dropping a good answer, hallucinated SKU/order id, wrong-worker handoff,
context loss mid-loop, and FINISH firing before all needed info is gathered.
