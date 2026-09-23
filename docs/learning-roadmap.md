# Learning Roadmap

This repository follows the supplied Foundation-to-Production learning sequence.
The course material is used as direction; this file records the project-specific
implementation plan rather than copying the source material.

## Current Stage: Foundation and Session 2

Completed or started:

- Python virtual environment and environment-backed configuration
- LangChain document loading, chunking, embeddings, and Chroma retrieval
- Grounded customer-service answers with source reporting
- Sequential LangGraph workflow: retrieve, then generate an answer
- Technology trade-off note and single-agent architecture note

Next deliverables:

- Add a router workflow for policy questions versus human escalation
- Create a small golden question set for answer and retrieval checks
- Compare sequential and router behavior in a short architecture report

## Planned Stages

### Agent Architecture

Add router, planner, and supervisor examples only when each pattern solves a
different customer-service requirement. Keep the single-agent path as the
baseline for cost, latency, and maintainability comparisons.

### Evaluation and Observability

Add golden questions with expected evidence, retrieval hit checks, answer-quality
reviews, latency, token usage, and failure logging. Establish pass/fail thresholds
before adding more orchestration complexity.

### Production Readiness

Add input validation, prompt-injection resistance, PII handling, retries and
timeouts, model fallbacks, document refresh behavior, and access boundaries.

### Economics and Architecture Review

Measure embedding and generation cost, context size, cache opportunities, and
model-routing options. Keep decisions in trade-off notes with alternatives,
assumptions, evidence, risks, and review triggers.