# RAG Foundation

This is the first customer-service application slice:

```text
question -> split policy documents -> embed and retrieve -> grounded answer
```

The implementation is shared in `mini_agent/rag.py` and
`mini_agent/workflow.py`. Policy files live in the root `documents/` folder so
later days can extend the same knowledge base.