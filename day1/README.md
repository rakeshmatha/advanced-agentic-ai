# Day 1: Foundation and Engineering Decisions

Day 1 establishes the Python and RAG foundation, then records the first
architecture choices for the customer-service assistant.

## Folders

- `foundation/`: environment configuration and a basic LLM call
- `rag/`: the first customer-service RAG exercise
- `engineering_decisions/`: decision matrix and trade-off notes

The reusable implementation remains in `mini_agent/`. Day folders contain
learning-facing entry points and artifacts, not duplicated framework code.

## Run the examples

```powershell
python -m day1.foundation.basic_chat
python -m day1.rag.ask "Can I return an unopened item?"
```