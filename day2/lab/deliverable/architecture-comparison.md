# Day 2 Deliverable: RAG + Architecture Decision

## RAG system evidence

`python -m day2.lab.rag_system "Can I return an unopened item?"` builds a FAISS
index from `docs/` and answers with sources (`customer-service-policy.md`,
`getting-started.md`). Pipeline: load → chunk (800/120) → embed
(`text-embedding-3-small`) → FAISS → retrieve k=4 → grounded answer.

## Architecture scores (IN01)

`architecture-decision --demo` (or `python -m day2.lab.decision_framework --demo`):

| Use case | Total | Override | Architecture |
| --- | --- | --- | --- |
| Automated Returns Processing | 7 | no | Traditional Software |
| Supplier Risk Intelligence | 21 | no | Agent |
| Store Performance Analytics Reporter | 17 | no | Workflow (Chain) |
| Customer Service Live Chat Assistant | 15 | YES | Hybrid (Agent + Workflow) |

Live chat scores in the workflow band but the hybrid override fires because
complexity is high (4) while latency and cost are constrained (2/2): a workflow
backbone handles simple traffic and a constrained agent handles the complex 15%.

## Technology choices

| Area | Choice | Rationale |
| --- | --- | --- |
| RAG components | LangChain | Reusable loaders, splitters, embeddings, retrievers |
| Vector store | FAISS | Simple local similarity search for the lab |
| Protocol | REST for this lab | One app, two HTTP APIs; MCP on Day 3 when tools are shared |
| Weather / demand / LLM | Buy | OpenWeatherMap, Tavily, OpenAI - not Walmart differentiators |
| Orchestration | Build Python-only | Two fetches + one prompt; buy a framework when the loop grows |

## Review triggers

Move a use case toward agent/hybrid when multi-step reasoning, dynamic tools, or
weekly-changing rules appear. Revisit RAG when documents grow or latency
tightens.
