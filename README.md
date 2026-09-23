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
%%{init: {"theme": "base", "themeVariables": {"fontFamily": "Segoe UI, sans-serif", "fontSize": "17px", "primaryTextColor": "#111827", "lineColor": "#64748b", "clusterBkg": "#ffffff", "clusterBorder": "#94a3b8"}}}%%
flowchart LR
    subgraph DAY1["DAY 1 | COMPLETE"]
        direction TB
        D1T["LEARN\nArchitecture patterns\nRAG vs fine-tuning\nREST API vs MCP"] --> D1B["BUILD\nLangChain + Chroma\nLangGraph RAG flow\nSource-grounded answers\nPATH: day1/lab/application/"] --> D1O["OUTPUT\nDecision matrix\nPolicy corpus\nPATH: day1/lab/deliverable/"]
    end
    subgraph DAY2["DAY 2 | CURRENT"]
        direction TB
        D2T["LEARN\nSingle vs multi-agent\nSequential vs router\nEscalation and handoffs"] --> D2B["BUILD\nRouter graph\nPolicy -> RAG\nAction -> human\nPATH: day2/lab/router.py"] --> D2O["OUTPUT\nPattern comparison\nRoute analysis\nPATH: day2/lab/deliverable/"]
    end
    subgraph DAY3["DAY 3 | PLANNED"]
        direction TB
        D3T["LEARN\nPlanner-executor\nSupervisor\nTools and MCP"] --> D3B["BUILD\nPlanner flow\nSupervisor flow\nFailure tests\nPATH: day3/lab/"] --> D3O["OUTPUT\nArchitecture report\nCost and latency\nPATH: day3/lab/deliverable/"]
    end
    subgraph DAY4["DAY 4 | PLANNED"]
        direction TB
        D4T["LEARN\nGolden datasets\nQuality metrics\nTracing and gates"] --> D4B["BUILD\nEvaluation harness\nEvidence checks\nScorecard\nPATH: day4/lab/"] --> D4O["OUTPUT\nEvaluation scorecard\nObservability design\nPATH: day4/lab/deliverable/"]
    end
    subgraph DAY5["DAY 5 | PLANNED"]
        direction TB
        D5T["LEARN\nGuardrails and PII\nResilience and cost\nDeployment"] --> D5B["BUILD\nControls and fallbacks\nCost model\nRisk register\nPATH: day5/lab/"] --> D5O["OUTPUT\nProduction checklist\nARB package\nPATH: day5/lab/deliverable/"]
    end

    DAY1 ~~~ DAY2 ~~~ DAY3 ~~~ DAY4 ~~~ DAY5

    classDef complete fill:#d8f3dc,stroke:#2d6a4f,color:#1b4332,stroke-width:3px,font-size:17px,font-weight:bold
    classDef current fill:#fff3bf,stroke:#e09f3e,color:#7f4f24,stroke-width:3px,font-size:17px,font-weight:bold
    classDef planned fill:#dbeafe,stroke:#3b82f6,color:#1e3a8a,stroke-width:3px,font-size:17px,font-weight:bold
    classDef deliverable fill:#f3e8ff,stroke:#7e22ce,color:#581c87,stroke-width:3px,font-size:17px,font-weight:bold
    class D1T,D1B complete
    class D1O,D2O,D3O,D4O,D5O deliverable
    class D2T,D2B current
    class D3T,D3B,D4T,D4B,D5T,D5B planned
    style DAY1 fill:#000000,stroke:#2d6a4f,stroke-width:3px,color:#ffffff
    style DAY2 fill:#000000,stroke:#e09f3e,stroke-width:3px,color:#ffffff
    style DAY3 fill:#000000,stroke:#3b82f6,stroke-width:3px,color:#ffffff
    style DAY4 fill:#000000,stroke:#3b82f6,stroke-width:3px,color:#ffffff
    style DAY5 fill:#000000,stroke:#3b82f6,stroke-width:3px,color:#ffffff
```

### Diagram Legend

| Visual | Meaning |
| --- | --- |
| Green | Completed learning and implementation |
| Yellow | Current learning and implementation |
| Blue | Planned learning and implementation |
| Purple | Day deliverable or review artifact |

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