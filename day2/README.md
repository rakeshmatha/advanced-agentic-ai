# Day 2: Agent Architecture

Status: **In progress**

Day 2 extends the Day 1 customer-service RAG into explicit agent architecture
and engineering decisions.

## Folders

- `topics/`: agent principles and orchestration patterns
- `lab/`: the sequential baseline, router implementation, and deliverable

## Run the Router Lab

```powershell
python -m day2.lab.router "Can I return an unopened item?"
python -m day2.lab.router "I need to change my delivery address."
```

## Session 2 Outputs

- Engineering decision notes: LangChain vs LangGraph vs Python-only.
- Build-vs-buy analysis for agent harnesses and in-house orchestration.
- Working sequential and router agent patterns.
- Final decision matrix and architecture comparison in `lab/deliverable/`.


Decision:
Python      -> application glue and tests
LangChain   -> RAG components
LangGraph   -> agent orchestration