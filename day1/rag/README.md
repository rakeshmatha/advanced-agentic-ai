# RAG Foundation

This is the first customer-service application slice:

```text
question -> split policy documents -> embed and retrieve -> grounded answer
```

The implementation is in `day1/application/rag.py` and
`day1/application/workflow.py`. Policy files live in this folder so later days
can add their own knowledge bases without mixing learning stages.