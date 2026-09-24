# Day 3 Lab

Day 3 class content: protocol choice (REST vs MCP), framework selection, agent
design, and the three orchestration patterns. All share the four Walmart tools in
`tools.py`. Tables use the shared helper in `_display.py`.

## IN03: REST vs MCP + framework bake-off

```bash
restmcp                 # REST vs MCP (boxed) + Python/LangChain/LangGraph bake-off
restmcp --protocol      # only the REST vs MCP tables
restmcp --frameworks    # only the framework comparison
restmcp "What should we stock if it rains all week?"
```

- **REST**: schema hand-written in the agent; a manual loop drives tool calls.
- **MCP**: launches `day3.lab.mcp_server` (real FastMCP), the client **discovers**
  the tools, and the LLM calls them through the MCP session.
- **Bake-off**: the same store question through Python-only, LangChain
  (`create_agent`), and a hand-built LangGraph state graph, comparing latency and
  control flow (a TCO decision).

The server can also run standalone:

```bash
python -m day3.lab.mcp_server
```

## IN04: single-agent vs multi-agent

```bash
singlemulti             # boxed single-vs-multi comparison on the test queries
singlemulti --chat      # talk to the multi-agent, see routing live
singlemulti "Where is my order WM-2024-002?"
```

Single agent = one LLM bound to all tools in a loop. Multi agent = a coordinator
that classifies PRODUCT vs SERVICE and delegates to a specialist with fewer tools.

## Interactive assistant

```bash
assistant               # chat with the router-backed Walmart assistant
assistant "Do you price match?"
```

Classify -> route (PRODUCT / SERVICE / ORDER) -> specialist tools -> answer.
`/exit` leaves the chat.

## IN05: orchestration patterns

```bash
sequential "What is the price of milk and is it in stock?"
router "Check my order WM-2024-002."
supervisor "Do you price match? I saw eggs cheaper at Target."
compare                 # all three on the shared query set (boxed table)
compare --pattern router
compare "Find chicken breast and tell me if I can pick it up today."
```

`compare` prints one boxed table: each query row shows every pattern's route and
latency, with a ✓ when the router intent matched the expected route.

All Day 3 labs need `OPENAI_API_KEY`; `restmcp` also uses the weather/Tavily keys.
