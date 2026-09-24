# Day 3 Deliverable: Orchestration Comparison

Homework from IN03 (REST vs MCP), IN04 (single vs multi-agent), and IN05
(sequential, router, supervisor). All share the four tools in `tools.py`
(`search_product`, `check_inventory`, `get_policy`, `get_order_status`).

## IN03: REST vs MCP

`python -m day3.lab.rest_mcp` runs both against the same store question.

| Approach | Where the schema lives | Live run |
| --- | --- | --- |
| REST | Hand-written in the agent | Called `store_weather` + `demand_trends`, ~9s |
| MCP | Owned by the FastMCP server | Client discovered `['store_weather', 'demand_trends']` and called them |

Use REST when one app owns the tool. Adopt MCP when several hosts must share the
same tools without copying schemas.

## IN04: single vs multi-agent

`python -m day3.lab.single_multi_agent`. Single agent binds all four tools and
loops. Multi agent routes PRODUCT vs SERVICE to a specialist with a smaller tool
set. Multi adds ~0.5-1s coordinator overhead but keeps each agent's context and
tool surface small (governance isolation).

## IN05: orchestration patterns (shared queries)

`python -m day3.lab.compare`. Expected router labels:

| Query | Expected route |
| --- | --- |
| Price of milk and stock | product |
| Return a TV bought 10 days ago | service |
| Check order WM-2024-002 | order |
| Chicken breast pickup today | product |
| Price match eggs at Target | service |

| Criterion | Sequential | Router | Supervisor |
| --- | --- | --- | --- |
| Query complexity | Fixed steps | Single-domain | Multi-domain |
| Latency | Highest (4 stages) | Lowest | Medium |
| Audit / quality gate | Yes | No | Transcript |
| Re-routing | No | No | Yes (loops to a cap) |
| Cost per query | Highest | Lowest | Medium |

## Recommendation by request type

| Request type | Choose | Why |
| --- | --- | --- |
| One policy or one order id | Router | One specialist, lowest cost |
| Product + inventory | Router product worker | Same tool set |
| Product + pickup/policy | Supervisor | Needs a second domain |
| Regulated, every step must run | Sequential | Quality gate is mandatory |

## Decision

Default production shape: **REST + a router over specialists**. Escalate only
when a second host, a second domain, or a mandatory audit step appears.

### Protocol (REST vs MCP)

| Situation | Decision |
| --- | --- |
| One app owns product, order, or weather tools | **REST** — schema lives in the agent, easy to log and version |
| A second host (Copilot, Cursor, another agent) needs the same catalog | **MCP** — server owns the schema; clients discover instead of copy |
| Tools change weekly and many consumers would drift | **MCP** — one source of truth beats N hand-written schemas |
| You need enterprise auth, SLAs, and existing API gateways | Stay on **REST** until MCP hosting is production-ready |

Retail system (`retail_multi_agent`) mapping we would actually ship: Product and Orders stay REST (internal
microservices). Inventory goes MCP (live stock shared by more than one host).
Policy stays RAG (documents, not an API).

### Agent split (single vs multi)

Stay **single-agent** while the tool count is small, intents overlap, and one
team owns the whole loop. Split into a **coordinator + specialists** when any of
these fire: context overload, skill mismatch (product vs policy), different
owners or permissions, a single failure domain that is too large, or work that
should run in parallel.

Do not split just because there are four tools. Split because governance or
accuracy demands a smaller tool surface per agent.

### Orchestration (sequential vs router vs supervisor)

| Request | Decision | Why this, not the others |
| --- | --- | --- |
| One policy, one order id, one product lookup | **Router** | One specialist. Sequential wastes three extra LLM calls. Supervisor is idle overhead. |
| Product + inventory on the same SKU | **Router** (product worker) | Same domain / same tool set. Supervisor only if inventory is a separate owner. |
| Product + stock + returns / pickup / price-match | **Supervisor** | Cross-domain. Router would drop the second and third parts. Sequential cannot re-route if a worker misses a SKU. |
| Refunds, regulated answers, every step must run | **Sequential** | Quality gate is mandatory. Router has no audit stage. Supervisor retries but does not guarantee a format/quality pass. |
| Unknown mix of traffic, most of it single-intent | **Router default**, supervisor as overflow | Cheapest happy path; escalate only when classify (or the user) signals multi-domain. |

Mis-route is the router's main cost — if PRODUCT vs SERVICE vs ORDER labels
blur, add a supervisor or a second classify pass rather than jumping straight
to sequential.

### Framework (Python vs LangChain vs LangGraph)

| Situation | Decision |
| --- | --- |
| Two fetches + one prompt, you own the loop | **Python-only** — max control, least magic |
| Reusable tools, prompts, retrievers, model swap | **LangChain** — TCO win once integrations multiply |
| Explicit state, retries, branching, HITL | **LangGraph** — router and supervisor graphs, not a linear chain |

Buy weather, search, and the LLM. Build the orchestrator in Python/LangGraph
because routing, caps (`MAX_STEPS`), and SKU handoff are Walmart-specific.

### Switch triggers (revisit this doc when…)

- A second consumer needs the same tools → REST to MCP.
- Tool count or owners diverge → single-agent to multi-agent.
- Queries regularly span two domains or FINISH fires early → router to supervisor.
- Compliance requires a quality gate on every answer → sequential (or sequential
  as a post-step after router/supervisor).
- Latency budget is missed on the supervisor loop → keep router for single-intent
  traffic; do not run supervisor on every request.

**One-line call:** Router + REST specialists in production; MCP where tools are
shared; supervisor only for multi-domain; sequential only when audit is
non-negotiable.
