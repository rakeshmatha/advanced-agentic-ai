# Day 4 Topics: Evaluation, Observability, and Debugging

## Outcome

Build a repeatable evaluation pipeline and use observability data to diagnose
failures in the customer-service RAG and agent workflows.

## Evaluation

- Create a golden dataset with representative questions, expected evidence,
	expected routes, and acceptable answer behavior.
- Run regression tests after prompt, model, retriever, or workflow changes.
- Measure retrieval hit rate, ranking quality, groundedness, answer quality,
	task success, escalation correctness, latency, and token cost.
- Define pass/fail thresholds and a go/no-go release gate.
- Use LLM-as-judge carefully with calibration examples and human review.

## Observability

- Decide what to log for requests, graph nodes, retrieval, model calls, and
	tool calls.
- Structure traces with request IDs, node names, timings, status, errors, and
	safe metadata.
- Identify slow steps, expensive steps, repeated failures, and quality drift.
- Compare Langfuse or Phoenix as observability options for agent workflows.

## Debugging

Trace a failed answer from the customer question through routing, retrieval,
prompt construction, model output, and source reporting. Separate retrieval
failure, orchestration failure, model failure, and data-quality failure.

## Day 4 Lab

Build a golden-test harness for the RAG plus agent system. Run it against the
current implementation, calculate a scorecard, and create a dashboard design
showing quality, latency, cost, and error rate per step.

## Deliverable

An evaluation scorecard with thresholds and a working observability design for
traces, metrics, debugging, and release decisions.