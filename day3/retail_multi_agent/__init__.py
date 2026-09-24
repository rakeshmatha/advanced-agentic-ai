"""Day 3 retail_multi_agent: a Walmart assistant with four specialists.

Four specialist agents, each with a different integration:
- Product   -> REST (internal Product Service)
- Inventory -> MCP  (Inventory MCP server)
- Orders    -> REST (internal Orders Service)
- Policy    -> RAG  (FAISS over policy docs)

Two LangGraph orchestrators over the same agents:
- Router     (single-agent per query)
- Supervisor (multi-agent loop until FINISH)
"""
