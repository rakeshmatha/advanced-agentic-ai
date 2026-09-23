# Day 1: Foundation and Engineering Decisions

Day 1 establishes the Python and RAG foundation, then records the first
architecture choices for the customer-service assistant.

## Folders

- `01_architecture_patterns/`: agent, workflow, and traditional software
- `02_rag_vs_finetuning_vs_prompting/`: technology selection framework
- `03_api_vs_mcp/`: integration selection framework
- `04_lab/`: two-use-case analysis exercise
- `05_deliverable/`: initial decision-matrix submission
- `foundation/`, `rag/`, and `engineering_decisions/`: runnable examples and supporting artifacts

The reusable implementation remains in `mini_agent/`. Day folders contain
learning-facing entry points and artifacts, not duplicated framework code.

## Run the examples

```powershell
python -m day1.foundation.basic_chat
python -m day1.rag.ask "Can I return an unopened item?"
```