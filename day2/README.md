# Day 2: RAG System + Architecture Decisions + API Intro

Status: **Complete**

Day 2 builds on Day 1 embeddings. You go from "text -> vector" to a full
**Retrieval-Augmented Generation** system, learn a framework for **deciding which
architecture** a problem needs (traditional / workflow / agent / hybrid), and
run the IN03 **build-vs-buy intro**: live weather + demand for a store manager,
then REST vs MCP, framework, and build vs buy. Agents, MCP, and orchestration
are Day 3.

## What you learn

1. **RAG system (LangChain + FAISS)** - load docs, chunk, embed, store/search in
   FAISS, and answer grounded in retrieved chunks with sources.
2. **Architecture decision framework (IN01)** - score a use case on five axes and
   get a recommendation, including the hybrid override.
3. **API / MCP / Frameworks / Build vs Buy intro (IN03)** - live OpenWeatherMap
   + Tavily for WMT-2847 Bengaluru, a Python-only stocking recommendation, then
   the three architect questions (REST vs MCP, framework, build vs buy).

## Source notebooks

- `Day2/1 RAG continued/4 RAG_system_using_LangChain_and_OpenAI.ipynb`
- `Day2/IN01_Architecture_Decision_Framework.ipynb`
- `Day2/IN03_API_MCP_Frameworks_Build_vs_Buy - Intro.ipynb`

## Folder layout

```text
day2/
  README.md                 <- you are here
  topics/README.md          concepts: RAG pipeline, five-axis model, APIs
  lab/
    rag_system.py           LangChain + FAISS RAG (chat + one-shot)
    decision_framework.py   IN01 five-axis architecture scorer
    build_vs_buy.py         IN03 intro: live APIs + REST/MCP/framework/build-vs-buy
    docs/                   knowledge base for RAG (md/txt/pdf)
    README.md               per-module run guide
    deliverable/
      architecture-comparison.md   RAG + architecture write-up
      README.md
```

## Prerequisites

- `.venv` created and dependencies installed (root `README.md`).
- `.env` keys:
  - `OPENAI_API_KEY` - required for RAG (embeddings + answers).
  - `OPENWEATHERMAP_API_KEY`, `TAVILY_API_KEY` - required for `build-vs-buy`.
- Models: chat `gpt-4o-mini`, embeddings `text-embedding-3-small`.
- Extra libs: `faiss-cpu`, `langchain-community`, `pypdf`, `requests`.

## Setup

```bash
cd advanced-agentic-ai
source ./activate
```

## Run the homework

```bash
rag                                    # interactive RAG chat over docs/
rag "Can I return an unopened item?"   # one-shot question
architecture-decision                  # type a use case; IN01 rules pick the architecture
architecture-decision --demo           # four class examples (homework evidence)
build-vs-buy                           # live stock rec + protocol/framework/build-vs-buy
build-vs-buy "What should we stock if it rains all week?"
```

Equivalent: `python -m day2.lab.rag_system --chat`,
`python -m day2.lab.decision_framework`, `python -m day2.lab.build_vs_buy`.
(Re-run `source ./activate` so `architecture-decision` and `build-vs-buy` load.)

### 1. RAG system

RAG = "ask your documents", so it runs as a **chat**. It builds the FAISS index
once, then for each question: embeds it, retrieves the top-4 chunks, answers only
from those chunks, and prints which files the chunks came from.

```bash
rag
you> Can I return an unopened item?
you> What if my item arrived damaged?
you> How many vacation days do I get?   # not in docs -> it should refuse
```

`/exit` leaves the chat. Add `.md`/`.txt`/`.pdf` files to `lab/docs/` to grow the
knowledge base. One-shot mode (`rag "..."`) is handy for homework evidence.

### 2. Architecture decision framework (IN01)

You type what you want to build. The model only **scores** five axes. The
Python rules in `decision_framework.py` then pick Traditional / Workflow /
Hybrid / Agent - the model does not choose the architecture.

```bash
architecture-decision
use case> Live chat that answers policy questions in under 2 seconds.
architecture-decision --demo
architecture-decision "Refund unopened returns automatically."
```

| Axis | Low (1) | High (5) |
| --- | --- | --- |
| Task complexity | Single step | Multi-step, dynamic |
| Latency tolerance | Real-time | Batch acceptable |
| Cost ceiling | Pennies/query | Dollars/query |
| Risk tolerance | Zero errors | Caught downstream |
| Update frequency | Rarely changes | Weekly |

Bands: **5-12** traditional, **13-18** workflow, **19-25** agent.
**Hybrid override:** `task_complexity >= 4` and (`latency <= 2` or `cost <= 2`).

### 3. Build vs Buy intro (IN03)

The class notebook's scenario: the store manager at **WMT-2847 Bengaluru** asks
what to stock today. The answer depends on **live** weather (OpenWeatherMap) and
demand (Tavily), not LLM memory. Then the notebook poses three architect
questions before any production code:

1. Protocol: REST vs MCP
2. Framework: Python-only vs LangChain vs LangGraph
3. Build vs Buy for each component

```bash
build-vs-buy
build-vs-buy "It will rain all week. What should we stock?"
```

This lab implements the **Python-only** path from the notebook (you pre-fetch,
then the LLM reasons). It prints the live signals, a stocking recommendation,
and the three decision tables. REST tools, a real MCP server, and LangGraph
agents are **Day 3**.

## Key takeaways

- RAG grounds answers in **your** documents and cites sources; it should refuse
  when the answer is not in context.
- Not every problem needs an agent - **score it first**; sometimes plain software
  or a fixed workflow is the right call.
- A constrained hybrid (workflow backbone + a small agent for the hard slice) fits
  high-complexity, tight-latency/cost cases.
- Real assistants need **live external data**, not just static docs.
- For two HTTP tools used by one app: **buy** the APIs, **build** a Python-only
  loop, stay on **REST**. Adopt MCP and a heavier framework when many agents
  share the same tools.

## Deliverable

See [`lab/deliverable/architecture-comparison.md`](lab/deliverable/architecture-comparison.md)
for the RAG evidence, the IN01 scores, and the technology choices.

## Where this leads

Day 3 turns the Day 2 API functions into **REST tools** and a real **MCP server**,
then designs **single vs multi-agent** systems and compares **orchestration
patterns** (sequential / router / supervisor).
