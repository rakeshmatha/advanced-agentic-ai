# Agent Architecture: Part 1

## Current Design: Single Agent

The current system has one bounded customer-service workflow:

```text
customer question -> retrieve policy chunks -> generate grounded answer
```

LangGraph makes the state and nodes explicit. The agent is intentionally not
autonomous: it cannot invent policy, call arbitrary tools, or change an order.
That boundary is appropriate for a first customer-service RAG application.

## Single-Agent Benefits

- Lower latency and token cost
- One prompt and one evaluation surface
- Easier debugging and tracing
- Clear responsibility for policy-grounded answers

## Multi-Agent Trade-Off

Multi-agent systems can separate specialist responsibilities such as intent
classification, order lookup, returns processing, and escalation. They also add
coordination state, handoff failures, more model calls, more evaluation cases,
and more difficult security boundaries.

## Design Rule

Start with one agent when the workflow is narrow and the knowledge source is
shared. Introduce a second specialist only when a separate responsibility has a
different tool, policy boundary, owner, or evaluation metric. Do not split an
agent merely to make the architecture look more advanced.

## Next Architecture Steps

1. Add an explicit answer-quality and escalation evaluation set.
2. Add a confidence or evidence check before returning an answer.
3. Add conversation history only after single-turn behavior is reliable.
4. Add specialist nodes for order lookup or escalation when real requirements demand them.