# Customer Service RAG

Python-only learning project using LangChain for RAG components and LangGraph
for workflow orchestration.

The learning work is organized by day under `day1/` through `day5/`. Day 1 is
complete; Day 2 is the current implementation phase.

## Layout

```text
day1/topics/            Combined Day 1 learning topics
day1/lab/               Day 1 runnable implementation and documents
day1/lab/deliverable/   Day 1 final decision matrix and output
day2/                   Day 2 agent architecture workspace
day3/                   Day 3 advanced orchestration workspace
day4/                   Day 4 evaluation and observability workspace
day5/                   Day 5 production readiness workspace
```

## Run

```powershell
.\venv\Scripts\Activate.ps1
python -m day1.lab.ask "Can I return an unopened item?"
```

Add `.md` or `.txt` files to `day1/lab/documents/` as the policy knowledge base grows.
See [day1/lab/deliverable/decision-matrix.md](day1/lab/deliverable/decision-matrix.md)
for the completed Day 1 design decision.

## Learning Plan

This project follows a foundation-to-production path for a customer-service AI
assistant. Each phase adds a capability and a reviewable engineering artifact.

## Learning Graph

```mermaid
flowchart TB
    subgraph DAY1["DAY 1 | COMPLETE: Foundation and decisions"]
        direction LR
        D1["LEARNED\nArchitecture patterns\nRAG vs fine-tuning vs prompting\nREST API vs MCP"] --> D1L["BUILT LOCALLY\nLangChain RAG + Chroma\nLangGraph retrieve -> answer\nSource-grounded policy answers\nday1/lab/application/"] --> D1O["DELIVERABLE\nDecision matrix\nPolicy corpus\nday1/lab/deliverable/"]
    end

    subgraph DAY2["DAY 2 | CURRENT: Agent architecture"]
        direction LR
        D2["LEARNING NOW\nSingle vs multi-agent\nSequential vs router\nTools, escalation, handoffs"] --> D2L["BUILDING LOCALLY\nclassify_request node\nPolicy -> Day 1 RAG\nAction -> human escalation\nday2/lab/router.py"] --> D2O["DELIVERABLE\nSequential vs router\nRoute and failure analysis\nday2/lab/deliverable/"]
    end

    subgraph DAY3["DAY 3 | PLANNED: Advanced orchestration"]
        direction LR
        D3["TO LEARN\nPlanner-executor\nSupervisor workflow\nTools, MCP, handoffs"] --> D3L["TO BUILD\nShared customer-service tools\nPlanner and supervisor flows\nTimeout and retry tests"] --> D3O["DELIVERABLE\nPattern comparison\nQuality, cost, latency, failures"]
    end

    subgraph DAY4["DAY 4 | PLANNED: Evaluation and observability"]
        direction LR
        D4["TO LEARN\nGolden datasets\nRetrieval and answer metrics\nLLM-as-judge, logs, traces"] --> D4L["TO BUILD\nGolden-test harness\nEvidence, route, timing, cost\nWorkflow traces and scorecard"] --> D4O["DELIVERABLE\nEvaluation scorecard\nPass/fail gates\nObservability design"]
    end

    subgraph DAY5["DAY 5 | PLANNED: Production readiness"]
        direction LR
        D5["TO LEARN\nGuardrails and PII\nPrompt-injection defense\nResilience, economics, deployment"] --> D5L["TO BUILD\nInput/output controls\nRetry and fallback tests\nCost, risk, rollback plan"] --> D5O["DELIVERABLE\nProduction checklist\nCost and risk package\nArchitecture Review Board"]
    end

    D1O --> D2
    D2O --> D3
    D3O --> D4
    D4O --> D5

    classDef complete fill:#d8f3dc,stroke:#2d6a4f,color:#1b4332
    classDef current fill:#fff3bf,stroke:#e09f3e,color:#7f4f24
    classDef planned fill:#dbeafe,stroke:#3b82f6,color:#1e3a8a
    classDef deliverable fill:#f3e8ff,stroke:#7e22ce,color:#581c87
    class D1,D1T,D1L complete
    class D1O,D2O,D3O,D4O,D5O deliverable
    class D2,D2T,D2L current
    class D3,D3T,D3L,D4,D4T,D4L,D5,D5T,D5L planned
```

### Day 1: Foundation and Engineering Decisions - Complete

- Refresh Python environments, model calls, prompts, context windows, and RAG.
- Build the first policy-grounded customer-service question-answering flow.
- Compare traditional software, workflows, and agents.
- Compare RAG, fine-tuning, and prompting using cost, latency, quality, and maintainability.
- Compare REST APIs and MCP for external capabilities.
- Analyze two business use cases and create the initial decision matrix.

Artifacts: [day1/](day1/), [decision matrix](day1/lab/deliverable/decision-matrix.md),
and the sequential workflow in `day1/lab/application/workflow.py`.

### Day 2: Agent Architecture - In Progress

- Compare workflows, single-agent systems, and multi-agent systems.
- Add sequential and router patterns for customer-service questions.
- Define tool boundaries, escalation behavior, and failure handling.
- Explain why added orchestration complexity is justified.

Artifacts: [day2/topics/](day2/topics/), [day2/lab/](day2/lab/), and
[day2/lab/deliverable/](day2/lab/deliverable/).

### Day 3: Advanced Orchestration - Planned

- Explore planner-executor and supervisor patterns.
- Compare built-in functions, custom tools, REST APIs, and MCP integration.
- Model timeouts, retries, hallucinations, context loss, and handoff failures.

Deliverable: compare multiple orchestration strategies using the same tools.

### Day 4: Evaluation and Observability - Planned

- Create a golden question set for retrieval and answer quality.
- Measure evidence hit rate, answer quality, task success, latency, and cost.
- Add structured logs and traces for retrieval, model calls, and tool use.
- Define regression thresholds and a go/no-go scorecard.

Deliverable: evaluation harness and observability design.

### Day 5: Production Readiness and Architecture Review - Planned

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