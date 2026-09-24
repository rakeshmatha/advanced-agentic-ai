# Applied Agentic AI - Day-by-Day Labs

Hands-on lab companion to the Walmart Applied Agentic AI course in
`Walmart-USA-21-22-23-28-29-September-2026`. **Each day folder contains only what
that day's class taught** - nothing pulled forward, nothing left behind. Every
day is self-contained and builds on the previous one.

Shared plumbing (env loading, OpenAI client) lives in `common/` so no day imports
another day.

## Layout

```text
common/     Shared config + OpenAI client (not a class day)
day1/       LLM mechanics, prompt engineering, embeddings (RAG prerequisite)
day2/       RAG system (LangChain + FAISS), architecture scorer, build-vs-buy intro
day3/       REST vs MCP (+ real MCP server), single/multi-agent, orchestration
day4/       Planned: evaluation and observability
day5/       Planned: production readiness and architecture review
```

## Learning Graph

```mermaid
flowchart LR
    subgraph DAY1["DAY 1 | COMPLETE"]
        direction TB
        D1T["LEARN\nLLM mechanics\nPrompt engineering\nEmbeddings"] --> D1B["BUILD\nToken and prompt labs\nEmbedding experiments\nPlain OpenAI SDK"] --> D1O["OUTPUT\nFoundation evidence\nRAG prerequisite"]
    end

    subgraph DAY2["DAY 2 | COMPLETE"]
        direction TB
        D2T["LEARN\nRAG systems\nArchitecture decisions\nAPIs and build-vs-buy"] --> D2B["BUILD\nLangChain + FAISS\nFive-axis scorer\nLive API integration"] --> D2O["OUTPUT\nRAG system\nArchitecture comparison"]
    end

    subgraph DAY3["DAY 3 | COMPLETE"]
        direction TB
        D3T["LEARN\nREST vs MCP\nSingle vs multi-agent\nOrchestration patterns"] --> D3B["BUILD\nREST tools + MCP server\nSpecialist agents\nSequential/router/supervisor"] --> D3O["OUTPUT\nWorking assistant\nOrchestration comparison"]
    end

    subgraph DAY4["DAY 4 | PLANNED"]
        direction TB
        D4T["LEARN\nEvaluation\nQuality metrics\nObservability"] --> D4B["BUILD\nEvaluation harness\nEvidence checks\nTracing and gates"] --> D4O["OUTPUT\nEvaluation scorecard\nObservability design"]
    end

    subgraph DAY5["DAY 5 | PLANNED"]
        direction TB
        D5T["LEARN\nGuardrails and PII\nResilience and cost\nDeployment"] --> D5B["BUILD\nControls and fallbacks\nCost model\nRisk register"] --> D5O["OUTPUT\nProduction checklist\nArchitecture review"]
    end

    DAY1 ~~~ DAY2 ~~~ DAY3 ~~~ DAY4 ~~~ DAY5

    classDef complete fill:#d8f3dc,stroke:#2d6a4f,color:#1b4332,stroke-width:3px,font-weight:bold
    classDef planned fill:#dbeafe,stroke:#3b82f6,color:#1e3a8a,stroke-width:3px,font-weight:bold
    classDef deliverable fill:#f3e8ff,stroke:#7e22ce,color:#581c87,stroke-width:3px,font-weight:bold

    class D1T,D1B,D2T,D2B,D3T,D3B complete
    class D1O,D2O,D3O,D4O,D5O deliverable
    class D4T,D4B,D5T,D5B planned

    style DAY1 fill:#f0fdf4,stroke:#2d6a4f,stroke-width:3px
    style DAY2 fill:#f0fdf4,stroke:#2d6a4f,stroke-width:3px
    style DAY3 fill:#f0fdf4,stroke:#2d6a4f,stroke-width:3px
    style DAY4 fill:#eff6ff,stroke:#3b82f6,stroke-width:3px
    style DAY5 fill:#eff6ff,stroke:#3b82f6,stroke-width:3px
```

### Diagram Legend

| Visual | Meaning |
| --- | --- |
| Green | Completed learning and implementation |
| Blue | Planned learning and implementation |
| Purple | Day deliverable or review artifact |

## Setup

```bash
cd advanced-agentic-ai
python3 -m venv .venv
source ./activate                 # activates .venv and loads short commands
pip install -r requirements.txt   # first time only
```

`source ./activate` needs `.env` with `OPENAI_API_KEY` (and
`OPENWEATHERMAP_API_KEY`, `TAVILY_API_KEY` for the live-API labs). PowerShell:
`. .\Activate.ps1`.

## Run each day

```bash
# Day 1 - foundations (plain OpenAI SDK)
mechanics        # tokenization, cost, context window, temperature
prompts          # zero-shot, few-shot, CoT, role, structured output
embeddings       # text -> vectors

# Day 2 - RAG + decisions
rag                                    # interactive RAG chat over docs/
rag "Can I return an unopened item?"   # one-shot
architecture-decision                  # describe a use case; IN01 picks architecture
build-vs-buy                           # live stock rec + REST/MCP/framework/build-vs-buy

# Day 3 - protocols, agents, orchestration
restmcp          # REST vs MCP + Python/LangChain/LangGraph bake-off
singlemulti      # single-agent vs coordinator + specialists
assistant        # interactive Walmart assistant (chat)
compare          # sequential vs router vs supervisor
```

Each command maps to `python -m dayN.lab.<module>`; the aliases load with
`source ./activate`.

## Progress

| Day | Status | Class notebooks covered |
| --- | --- | --- |
| Day 1 | Complete | LLM mechanics + prompts; RAG prerequisites (embeddings) |
| Day 2 | Complete | RAG system (LangChain+FAISS); IN01 architecture; IN03 build-vs-buy intro |
| Day 3 | Complete | IN03 REST vs MCP; IN04 single/multi-agent; IN05 orchestration |
| Day 4 | Planned | Evaluation and observability |
| Day 5 | Planned | Production readiness and architecture review |

Each day's `topics/` explains what was taught; each `lab/deliverable/` holds the
reviewable artifact for that day.
