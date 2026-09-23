# Day 2 Lab

The lab implements and compares two Day 2 agent patterns using the Day 1
customer-service RAG capability: a sequential agent and a router agent.

## Sequential Agent

```powershell
python -m day2.lab.sequential "Can I return an unopened item?"
```

Flow:

```text
question -> policy answer -> response with sources
```

## Router Agent

```powershell
python -m day2.lab.router "Can I return an unopened item?"
python -m day2.lab.router "I need to change my delivery address."
```

Flow:
The router has two explicit paths:

```text
question -> classify -> policy RAG answer
                  -> human escalation
```

The classifier is deliberately simple for learning. A later version can use a
model-based intent classifier after we add evaluation data.