# Customer Service RAG

Python-only learning project using LangChain for RAG components and LangGraph
for workflow orchestration.

The learning work is organized by day under `day1/`. The reusable application
implementation stays in `mini_agent/` so later day examples can build on the
same customer-service system.

## Layout

```text
documents/              Customer-service policies in Markdown or text
mini_agent/config.py    Environment-backed settings
mini_agent/rag.py       Loading, chunking, and Chroma persistence
mini_agent/workflow.py  LangGraph retrieval and answer nodes
docs/                   Architecture decisions and learning notes
main.py                 Command-line entry point
day1/                   Day 1 examples and decision artifacts
```

## Run

```powershell
.\venv\Scripts\Activate.ps1
python main.py "Can I return an unopened item?"
```

Add `.md` or `.txt` files to `documents/` as the policy knowledge base grows.
See [docs/technology-tradeoffs.md](docs/technology-tradeoffs.md) and
[docs/agent-architecture.md](docs/agent-architecture.md) for the design notes.