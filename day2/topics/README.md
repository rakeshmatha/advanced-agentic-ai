# Day 2 Topics: Agent Architecture

## Single Agent vs Multi-Agent

Start with one bounded agent when the workflow, knowledge source, and policy
boundary are shared. Add specialists only when they have a distinct tool,
responsibility, owner, or evaluation metric.

Multi-agent systems can separate intent classification, order lookup, returns,
and escalation. They also add handoff failures, coordination state, model
calls, latency, and security boundaries.

## Orchestration Patterns

| Pattern | Flow | Use when |
| --- | --- | --- |
| Sequential | A -> B -> C | Steps are predictable |
| Router | Classify -> specialist | Requests need different paths |
| Planner-executor | Plan -> execute steps | Tasks need dynamic decomposition |
| Supervisor | Supervisor -> specialists -> supervisor | Multiple specialists need coordination |

## Day 2 Decision

Keep the Day 1 sequential RAG flow as the baseline. Add a router for the first
branch: answer approved policy questions with RAG, or escalate unsupported and
action-oriented requests to human support.

## Design Questions

- What state must survive between nodes?
- What happens when a route is uncertain?
- Which tools can each specialist call?
- How are timeouts, retries, and handoffs observed?