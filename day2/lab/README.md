# Day 2 Lab

Day 2 class content: a full RAG system, the architecture decision framework, and
the live build-vs-buy intro.

## RAG system (LangChain + FAISS)

```bash
python -m day2.lab.rag_system                 # interactive chat
python -m day2.lab.rag_system --chat          # same
python -m day2.lab.rag_system "Can I return an unopened item?"
```

Loads `docs/`, splits into chunks, embeds with `text-embedding-3-small`, stores
and searches in FAISS, then answers grounded in the retrieved chunks with
sources. The chat builds the index once, then each question retrieves top-4
chunks and prints which files they came from. `/exit` leaves the chat.

Add `.md`, `.txt`, or `.pdf` files to `docs/` to grow the knowledge base.

## Architecture decision framework (IN01)

```bash
architecture-decision
architecture-decision "Live chat that answers policy questions in under 2 seconds."
architecture-decision --demo
```

Type a use case in plain English. The model scores the five axes (1-5). The
IN01 **code** then picks Traditional / Workflow / Hybrid / Agent. `/demo`
prints the four class examples; `/exit` quits.

## Build vs Buy intro (IN03)

```bash
build-vs-buy
build-vs-buy "It will rain all week. What should we stock?"
```

Matches the class notebook: store WMT-2847 Bengaluru, live OpenWeatherMap +
Tavily, a Python-only stocking recommendation, then three decision tables
(REST vs MCP, framework, build vs buy). Needs `OPENWEATHERMAP_API_KEY` and
`TAVILY_API_KEY`. MCP + LangGraph agents are Day 3.
