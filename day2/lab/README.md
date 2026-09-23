# Day 2 Lab

The lab compares the Day 1 sequential RAG workflow with a router workflow.
The router has two explicit paths:

```text
question -> classify -> policy RAG answer
                  -> human escalation
```

The classifier is deliberately simple for learning. A later version can use a
model-based intent classifier after we add evaluation data.