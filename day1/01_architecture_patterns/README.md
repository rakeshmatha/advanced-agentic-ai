# 01: AI Application Architecture Patterns

## Concepts

| Pattern | Best fit | Strength | Main risk |
| --- | --- | --- | --- |
| Traditional software | Deterministic rules and stable inputs | Predictable and testable | Cannot handle open-ended language well |
| Workflow | Known steps with controlled branching | Observable and maintainable | Less flexible for novel tasks |
| Agent | Dynamic decisions and tool selection | Flexible for ambiguous tasks | Higher cost, latency, and failure surface |

## Customer-Service Application

The first release is a RAG workflow rather than a fully autonomous agent:

```text
question -> retrieve approved policy -> generate answer -> cite sources
```

This is the right starting point because customer-service policy answers need
traceability and predictable behavior. Agent behavior can be added later for
tool selection, order lookup, or escalation.

## Exercise

Classify two use cases as traditional software, workflow, or agent. Record the
decision, assumptions, risks, and the signal that would justify changing it.