# Day 1 Topics: LLM Mechanics, Prompt Engineering, RAG Prerequisites

What the instructor taught on Day 1. Nothing here depends on later days.

Source notebooks:
- `Day1/01_LLM_Mechanics_and_Prompt_Engineering.ipynb`
- `Day1/02 RAG Begins/3 RAG_Basic Prerequisites.ipynb`

## 1. LLM Mechanics

An LLM reads **tokens**, not words. Cost and context limits are measured in
tokens. At `$0.150` per 1M input tokens for `gpt-4o-mini`, wasted prompt text
matters at Walmart scale.

- **Tokenization**: common words are one token; SKUs and code split into many.
- **Context window**: the model only "remembers" the history you pass in.
- **Temperature**: 0.0 is deterministic; higher is more random. Use the lowest
  temperature that meets quality.

Runnable: `python -m day1.lab.mechanics`

## 2. Prompt Engineering Patterns

| Pattern | Use it when | Walmart example in lab |
| --- | --- | --- |
| Zero-shot | Common task, simple format | Ticket severity |
| Few-shot | Domain format the model may miss | Feedback → JSON |
| Chain-of-thought | Multi-step reasoning | Reorder decision with math |
| Role prompting | Audience and tone matter | Architect / Risk / Finance |
| Structured output | Downstream needs a schema | Incident → Pydantic |

Runnable: `python -m day1.lab.prompts`

## 3. RAG Prerequisites (embeddings)

Text becomes a fixed-length vector (`text-embedding-3-small` → 1536 dims).
Similar meaning lands nearby, which is what retrieval uses. The **full RAG
pipeline is Day 2**, not Day 1.

Runnable: `python -m day1.lab.embeddings`

## Day 1 takeaway

Learn to control the model (tokens, prompts) and turn text into vectors before
building RAG or agents in later days.
