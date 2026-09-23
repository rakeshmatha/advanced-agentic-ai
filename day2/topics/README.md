# Day 2 Topics: Engineering Decisions and Agent Architecture

## Session Outcome

Complete a technology selection and design a basic customer-service agent
system that can be explained during an architecture review.

## Engineering Decisions

### LangChain vs LangGraph vs Python-only

| Choice | Strength | Cost or risk | Day 2 position |
| --- | --- | --- | --- |
| Python-only | Maximum control and fewest dependencies | More orchestration and reliability code to own | Use for glue and tests |
| LangChain | Reusable model, prompt, retriever, and tool integrations | Fast-moving APIs and dependency upgrades | Use for RAG components |
| LangGraph | Explicit state, nodes, branching, and handoffs | More structure than a simple function | Use for agent workflows |

Evaluate each choice using complexity, maintainability, platform support, total
cost of ownership, latency, observability, and team skills.

### Build vs Buy

- In-house orchestration gives control over policy behavior, data boundaries,
	integrations, and evaluation, but the team owns reliability and operations.
- Off-the-shelf agent or harness systems can accelerate a demo and provide
	hosted operations, but may add lock-in, recurring cost, and less control.

For this learning project, build in-house because orchestration and trade-off
reasoning are the learning objectives.

### Trade-Off Note

A review-ready note records the decision, alternatives, assumptions, evidence,
risks, consequences, and triggers that would cause the decision to change.

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

## Tool Integration Practice

Day 2 now applies the router pattern to real tool boundaries:

- OpenWeatherMap for weather questions
- Tavily for web research questions
- Day 1 RAG for approved policy questions
- Human escalation for account or order actions

This demonstrates why a router can be more useful than one general-purpose
agent: each route has a narrower capability and clearer ownership.