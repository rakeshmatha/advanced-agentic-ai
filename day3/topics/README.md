# Day 3 Topics: Advanced Orchestration and Evaluation

## Outcome

Design more complex agent orchestrations and understand how to measure their
performance and failure behavior.

## Advanced Orchestration

- Planner-executor workflows for decomposing a request into tasks.
- Supervisor or hierarchical workflows for coordinating specialist agents.
- Tool integration using built-in tools, custom Python functions, REST APIs,
	and MCP servers.
- Agent-to-agent communication, handoffs, and shared state.
- Failure scenarios: timeouts, retries, hallucinations, context loss, and
	incomplete handoffs.

## Evaluation Foundations

- Why ad-hoc examples are not enough to assess an agent system.
- Output-level checks such as groundedness, hallucination, and safety.
- Retrieval-level checks such as hit rate and reciprocal rank.
- Agent-level checks such as task success, correct routing, and escalation.
- LLM-as-judge: useful signals, calibration needs, bias, and cost.

## Day 3 Lab

Use the same customer-service tools and questions to compare three orchestration
approaches:

1. Planner-executor
2. Supervisor or hierarchical workflow
3. Router workflow

Record answer quality, route correctness, latency, token usage, tool failures,
and escalation behavior for each approach.

## Deliverable

An architecture comparison report showing which pattern is best for each request
type, with evidence, failure modes, cost, latency, and maintainability trade-offs.