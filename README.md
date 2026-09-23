# Customer Service RAG

Python-only learning project using LangChain for RAG components and LangGraph
for workflow orchestration.

The learning work is organized by day under `day1/` through `day5/`. Day 1
contains the current runnable customer-service RAG application.

## Layout

```text
day1/application/       Day 1 configuration, RAG, and LangGraph workflow
day1/                   Day 1 examples and decision artifacts
day2/                   Day 2 agent architecture workspace
day3/                   Day 3 advanced orchestration workspace
day4/                   Day 4 evaluation and observability workspace
day5/                   Day 5 production readiness workspace
```

## Run

```powershell
.\venv\Scripts\Activate.ps1
python -m day1.rag.ask "Can I return an unopened item?"
```

Add `.md` or `.txt` files to `day1/rag/documents/` as the policy knowledge base grows.
See [day1/engineering_decisions/decision-matrix.md](day1/engineering_decisions/decision-matrix.md)
for the current design notes.

## Learning Plan

This project follows a foundation-to-production path for a customer-service AI
assistant. Each phase adds a capability and a reviewable engineering artifact.

### Day 1: Foundation and Engineering Decisions

- Refresh Python environments, model calls, prompts, context windows, and RAG.
- Build the first policy-grounded customer-service question-answering flow.
- Compare traditional software, workflows, and agents.
- Compare RAG, fine-tuning, and prompting using cost, latency, quality, and maintainability.
- Compare REST APIs and MCP for external capabilities.
- Analyze two business use cases and create the initial decision matrix.

Artifacts: [day1/](day1/), [decision matrix](day1/engineering_decisions/decision-matrix.md),
and the sequential workflow in `day1/application/workflow.py`.

### Day 2: Agent Architecture

- Compare workflows, single-agent systems, and multi-agent systems.
- Add sequential and router patterns for customer-service questions.
- Define tool boundaries, escalation behavior, and failure handling.
- Explain why added orchestration complexity is justified.

Deliverable: working agent patterns plus an architecture comparison note.

### Day 3: Advanced Orchestration

- Explore planner-executor and supervisor patterns.
- Compare built-in functions, custom tools, REST APIs, and MCP integration.
- Model timeouts, retries, hallucinations, context loss, and handoff failures.

Deliverable: compare multiple orchestration strategies using the same tools.

### Day 4: Evaluation and Observability

- Create a golden question set for retrieval and answer quality.
- Measure evidence hit rate, answer quality, task success, latency, and cost.
- Add structured logs and traces for retrieval, model calls, and tool use.
- Define regression thresholds and a go/no-go scorecard.

Deliverable: evaluation harness and observability design.

### Day 5: Production Readiness and Architecture Review

- Add input validation, prompt-injection defenses, PII handling, retries,
  timeouts, fallbacks, and access controls.
- Optimize tokens, context size, caching, model selection, and operating cost.
- Document deployment, rollback, incident response, risks, and mitigations.
- Defend architecture choices using evidence rather than preference.

Deliverable: production-readiness checklist and architecture review package.

### Completion Criteria

The system is ready for the next phase when it can answer supported policy
questions with evidence, escalate unsupported questions, pass a golden test set,
report latency and cost, and explain its technology choices in a trade-off note.