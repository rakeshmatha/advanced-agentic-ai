# Day 1 Decision Matrix

Use case: answer customer-service questions from approved policy documents.

| Approach | Quality | Complexity | Cost and latency | Maintainability | Decision |
| --- | --- | --- | --- | --- | --- |
| Prompt only | Weak for changing policy facts | Low | Low | Low policy traceability | Reject |
| Fine-tuning | Can learn style, not a live policy source | High | Higher training and update cost | Harder policy refresh | Defer |
| LangChain RAG | Good evidence access and source reporting | Medium | Embedding plus model calls | Good component reuse | Select |
| LangGraph RAG | Same RAG quality with explicit state and branching | Medium-high | Small orchestration overhead | Strong path to escalation | Select as workflow layer |
| Python-only RAG | Full control | Medium-high custom code | Potentially low runtime cost | More code owned by the team | Use for glue and tests |

## Assumptions

- Policy documents are the source of truth.
- The first release is single-turn and read-only.
- Unsupported questions should escalate instead of being guessed.
- A small local Chroma store is suitable for learning and prototyping.

## Review Triggers

Revisit the selection when order lookup, write actions, multi-turn memory,
high-volume ingestion, strict latency targets, or production governance become
requirements.