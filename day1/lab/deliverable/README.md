# Day 1 Deliverable

Reflection on what Day 1 taught, with evidence from the lab runs.

## What we learned

1. **Tokens drive cost and limits.** `SKU-7829341-B` becomes 6 tokens; a verbose
   system prompt was 51 tokens vs 15 for a concise one. Same meaning, ~3x cost.
2. **Context is memory.** Without history the model cannot recall the SKU-7829
   threshold; with history passed in, it answers "500 units".
3. **Temperature controls randomness.** At 0.0 the three runs were identical; at
   1.2 they diverged. Production uses the lowest temperature that meets quality.
4. **Prompt patterns make output reliable.** Zero-shot, few-shot, chain-of-thought,
   role prompting, and structured output each fit a different task.
5. **Embeddings are the RAG prerequisite.** Every text maps to a 1536-dim vector;
   similarity is what retrieval will use on Day 2.

## Evidence

- `python -m day1.lab.mechanics`
- `python -m day1.lab.prompts`
- `python -m day1.lab.embeddings`
