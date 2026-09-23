# Day 5 Topics: Production Readiness and Architecture Review

## Outcome

Prepare the customer-service AI system for production review by addressing
safety, reliability, cost, operations, and governance.

## Production Readiness

- Input validation, output guardrails, and policy-grounded response controls.
- Prompt-injection defense and separation of instructions from retrieved data.
- PII detection, minimization, redaction, retention, and access control.
- Timeouts, retries, circuit breakers, fallbacks, and graceful escalation.
- Scaling, concurrency, document refreshes, deployment, rollback, and incident
	response.

## AI Economics

- Token economics for prompts, retrieved context, embeddings, and outputs.
- Context-window management and retrieval-size controls.
- Caching repeated embeddings, retrieval results, or safe responses.
- Model routing based on quality, latency, and cost requirements.
- FinOps controls, budgets, usage thresholds, and cost alerts.

## Architecture Defence

Prepare to explain and defend:

- Why the system is a workflow, agent, or traditional application.
- Why the selected orchestration pattern and tools fit the use case.
- How quality is evaluated and where the go/no-go gate is.
- Projected cost, optimization levers, deployment model, and rollback plan.
- Security, hallucination, privacy, drift, and operational risks.

## Day 5 Lab

Create a production-readiness package for the customer-service assistant. Add a
risk register, cost model, deployment and incident-response outline, and an
architecture review checklist.

## Deliverable

An architecture review package that defends the major technical decisions under
quality, cost, latency, security, governance, and operational pressure.