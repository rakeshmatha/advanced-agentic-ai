# Day 1: Foundation - LLM Mechanics, Prompts, RAG Prerequisites

Status: **Complete**

Day 1 is the foundation day. It covers how an LLM actually works (tokens, cost,
memory, temperature), the core prompt-engineering patterns, and the first step
toward RAG (turning text into embedding vectors). Everything uses the **plain
OpenAI SDK** - no LangChain or LangGraph yet (those start Day 2).

## What you learn

1. **LLM mechanics** - tokenization, token cost, the context window (memory), and
   temperature (randomness).
2. **Prompt engineering** - zero-shot, few-shot, chain-of-thought, role prompting,
   and structured output (Pydantic).
3. **RAG prerequisite** - embeddings: text becomes a fixed-length vector, and
   similar meaning lands nearby. (The full RAG pipeline is Day 2.)

## Source notebooks

- `Day1/01_LLM_Mechanics_and_Prompt_Engineering.ipynb`
- `Day1/02 RAG Begins/3 RAG_Basic Prerequisites.ipynb`

## Folder layout

```text
day1/
  README.md              <- you are here
  topics/README.md       what was taught (concepts + tables)
  lab/
    mechanics.py         1.1-1.3 tokens, cost, context, temperature
    prompts.py           2.1-2.5 five prompt patterns
    embeddings.py        text -> vector (RAG prerequisite)
    README.md            per-module run guide
    deliverable/README.md   Day 1 reflection / evidence
```

## Prerequisites

- `.venv` created and dependencies installed (see the root `README.md`).
- `.env` with `OPENAI_API_KEY`. Tokenization/token-cost work **without** a key;
  everything else calls OpenAI.
- Model used: `gpt-4o-mini`; embeddings: `text-embedding-3-small`.

## Setup

```bash
cd advanced-agentic-ai
source ./activate     # activates .venv and loads the short commands
```

## Run the homework (scripted demos)

```bash
mechanics     # 1.1-1.3 tokenization, cost, context window, temperature
prompts       # 2.1-2.5 zero-shot, few-shot, CoT, role, structured output
embeddings    # 02 RAG Begins: text -> embedding vectors
```

Equivalent without aliases: `python -m day1.lab.mechanics`, etc.

### What each demo prints

| Command | You should see |
| --- | --- |
| `mechanics` | Token counts for Walmart text/SKUs/code, verbose-vs-concise prompt cost, a with/without-memory answer, and the same prompt at temperature 0.0 / 0.5 / 1.2 |
| `prompts` | Ticket severity (zero-shot), feedback -> JSON (few-shot), reorder with/without CoT, three role answers, and a soaked-pallet incident parsed into a Pydantic schema |
| `embeddings` | A 1536-length vector preview for short/medium/long text |

## Try it yourself (interactive `--chat`)

Each lab also has a chat mode so you can use your own input instead of only the
canned demo:

```bash
mechanics --chat      # multi-turn chat; live token count + cost + memory each turn
mechanics "SKU-123"   # one-shot: tokenize + price any text (no API key needed)
prompts --chat        # pick a pattern, then run it on text you type
embeddings --chat     # embed your text; see cosine similarity to earlier entries
```

Commands inside a chat: `/exit` quits; `/reset` clears memory (mechanics chat).

## Key takeaways

- Cost and context limits are measured in **tokens**, not words; SKUs/code cost
  more tokens than plain text.
- The model only "remembers" the history you pass in - that history *is* the
  context window.
- Use the **lowest temperature** that still meets quality.
- Pick the prompt pattern to fit the task: examples for format (few-shot),
  reasoning steps for math (CoT), a schema when downstream code needs structure.
- Embeddings turn meaning into geometry, which is what RAG retrieval uses next.

## Deliverable

See [`lab/deliverable/README.md`](lab/deliverable/README.md) for the Day 1
reflection and evidence.

## Where this leads

Day 2 uses these embeddings to build a full **RAG system** (LangChain + FAISS),
adds an **architecture decision framework**, and introduces **live APIs**.
