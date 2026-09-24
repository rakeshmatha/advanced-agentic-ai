# Day 1 Lab

Day 1 class content, implemented with the **plain OpenAI SDK** exactly like the
instructor notebooks. No LangChain or LangGraph on Day 1.

| Notebook section | Module | Command |
| --- | --- | --- |
| 1.1 Tokenization + token cost | `mechanics.py` | `python -m day1.lab.mechanics` |
| 1.2 Context window (memory) | `mechanics.py` | (same run) |
| 1.3 Temperature 0.0 / 0.5 / 1.2 | `mechanics.py` | (same run) |
| 2.1 Zero-shot ticket severity | `prompts.py` | `python -m day1.lab.prompts` |
| 2.2 Few-shot JSON extraction | `prompts.py` | (same run) |
| 2.3 Chain-of-thought reorder | `prompts.py` | (same run) |
| 2.4 Role prompting (3 roles) | `prompts.py` | (same run) |
| 2.5 Structured output (Pydantic) | `prompts.py` | (same run) |
| 02 RAG Begins: embeddings | `embeddings.py` | `python -m day1.lab.embeddings` |

All three require `OPENAI_API_KEY` in `.env` (tokenization prints offline).

## Interactive mode

Every module also takes `--chat` so you can test with your own input instead of
the scripted examples:

| Command | What you do |
| --- | --- |
| `python -m day1.lab.mechanics --chat` | Chat with memory; each turn prints tokens in/out + cost |
| `python -m day1.lab.mechanics "your text"` | One-shot tokenize + price (no key needed) |
| `python -m day1.lab.prompts --chat` | Choose a pattern, then run it on text you type |
| `python -m day1.lab.embeddings --chat` | Embed your text; see cosine similarity to earlier texts |

`/exit` leaves a chat; `/reset` clears memory in the mechanics chat.

The full RAG pipeline (LangChain + FAISS) is **Day 2**; agent orchestration is
**Day 3**. Day 1 stays limited to mechanics, prompts, and embeddings.
