# Technology Selection and Trade-Off Note

## Decision

Use Python with LangChain for reusable LLM and retrieval components, and
LangGraph for explicit workflow orchestration. Start with one customer-service
agent and a local Chroma store. Keep provider-specific code behind the existing
settings and workflow modules.

## Options Considered

| Option | Strengths | Costs and risks | Decision |
| --- | --- | --- | --- |
| Python only | Small dependency surface and maximum control | More prompt, retrieval, state, retry, and tracing code to maintain | Use for application glue and tests |
| LangChain | Standard integrations for models, loaders, retrievers, prompts, and vector stores | Fast-moving APIs and dependency upgrades | Select for RAG building blocks |
| LangGraph | Explicit stateful graphs, checkpoints, branching, and human-in-the-loop support | More structure than a simple function call | Select for workflow orchestration |
| Off-the-shelf agent platform | Faster initial demo and hosted operations | Vendor lock-in, recurring cost, limited control over policy behavior | Defer until requirements justify it |
| In-house orchestration | Full control of behavior, data, and integration boundaries | The team owns reliability, evaluation, security, and operations | Select for this learning phase |

## Trade-Offs

The additional LangChain and LangGraph complexity is justified because the
learning goal includes retrieval, agent state, and future routing. A Python-only
prototype would be cheaper initially, but would make the orchestration concepts
less explicit and increase custom maintenance as escalation and tool use arrive.

The first implementation deliberately avoids multi-agent coordination. A single
workflow is easier to test, cheaper to run, and easier to audit for customer
support policy compliance.

## Review Triggers

Revisit this decision if the system needs durable conversations, multiple tools,
human approval steps, strict latency budgets, high-volume ingestion, or a hosted
platform with operational guarantees.