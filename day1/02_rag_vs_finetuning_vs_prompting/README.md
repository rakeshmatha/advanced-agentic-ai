# 02: RAG vs Fine-Tuning vs Prompting

| Approach | Use it when | Cost and latency | Maintainability |
| --- | --- | --- | --- |
| Prompting | Behavior or format can be changed through instructions | Lowest setup cost; one model call | Easy to update, limited factual memory |
| RAG | Facts change and must be tied to source documents | Embedding plus retrieval and model calls | Policy updates are straightforward |
| Fine-tuning | Consistent behavior or domain style needs model adaptation | Training cost plus model inference | Harder to update and evaluate for live facts |

## Customer-Service Decision

Use RAG for approved policies because policy documents are the source of truth.
Use prompting for tone, refusal, and escalation behavior. Defer fine-tuning
until evaluation shows that prompting and retrieval cannot meet the quality
target.

## Lab

Compare the same customer question using prompting only and RAG. Record answer
quality, evidence, latency, token usage, and maintenance implications.