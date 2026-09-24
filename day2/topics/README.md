# Day 2 Topics: RAG System, Architecture Decisions, API Intro

What the instructor taught on Day 2. Builds on Day 1 embeddings; orchestration
and MCP are Day 3.

## 1. RAG System (LangChain + FAISS)

The full Retrieval-Augmented Generation pipeline:

1. Load documents (PDF / md / txt).
2. Split into overlapping chunks.
3. Embed each chunk with OpenAI embeddings.
4. Store and search vectors in FAISS.
5. Retrieve top-k chunks and answer grounded in them, with sources.

RAG is chosen when facts change and must be tied to source documents, versus
prompting (behavior/format) or fine-tuning (style, not live facts).

Runnable: `python -m day2.lab.rag_system` (chat) or pass a one-shot question.

## 2. Architecture Decision Framework (IN01)

Score each use case 1-5 on five axes. Higher pushes toward agents.

| Axis | Score 1 | Score 5 |
| --- | --- | --- |
| Task complexity | Single step | Multi-step, dynamic |
| Latency tolerance | Real-time | Batch acceptable |
| Cost ceiling | Pennies/query | Dollars/query |
| Risk tolerance | Zero errors | Caught downstream |
| Update frequency | Rarely changes | Weekly |

Bands: 5-12 traditional, 13-18 workflow, 19-25 agent. **Hybrid override:**
`task_complexity >= 4` and (`latency <= 2` or `cost <= 2`).

Runnable: `architecture-decision` (type a use case) or `--demo` for the class examples.

## 3. API / MCP / Build vs Buy Intro (IN03 intro)

The store manager at WMT-2847 Bengaluru asks what to stock today. That needs
live data, not LLM memory:

- OpenWeatherMap for weather-driven demand
- Tavily for market/demand signals

Then three architect questions (Day 2 poses them; Day 3 implements MCP/LangGraph):

1. Protocol: REST vs MCP
2. Framework: Python-only vs LangChain vs LangGraph
3. Build vs Buy for weather, demand, LLM, orchestration, shared tools

Runnable: `build-vs-buy` (chat) or pass a store-manager question.
