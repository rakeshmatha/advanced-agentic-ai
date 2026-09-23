# Day 1 Topics

Day 1 establishes the technology choices for the customer-service assistant.
The three topics below are studied together and applied in the lab.

## 1. AI Application Architecture Patterns

| Pattern | Best fit | Strength | Main risk |
| --- | --- | --- | --- |
| Traditional software | Deterministic rules and stable inputs | Predictable and testable | Limited language flexibility |
| Workflow | Known steps with controlled branching | Observable and maintainable | Less flexible for novel tasks |
| Agent | Dynamic decisions and tool selection | Flexible for ambiguous tasks | Higher cost, latency, and failure surface |

For the first release, customer-service policy questions use a controlled RAG
workflow: retrieve approved policy, generate an answer, and cite sources. Agent
behavior can be added later for order lookup or escalation.

## 2. RAG vs Fine-Tuning vs Prompting

| Approach | Use it when | Cost and latency | Maintainability |
| --- | --- | --- | --- |
| Prompting | Behavior or format changes through instructions | Lowest setup cost; one model call | Easy to update, limited factual memory |
| RAG | Facts change and must be tied to source documents | Embedding plus retrieval and model calls | Policy updates are straightforward |
| Fine-tuning | Consistent behavior or style needs model adaptation | Training cost plus model inference | Harder to update for live facts |

Use RAG for approved policies because policy documents are the source of truth.
Use prompting for tone, refusal, and escalation. Defer fine-tuning until testing
shows that prompting and retrieval cannot meet the quality target.

## 3. REST API vs MCP

| Option | Best fit | Strength | Trade-off |
| --- | --- | --- | --- |
| REST API | One application owns a stable service contract | Simple, familiar, secure, and monitorable | Each integration needs custom wiring |
| MCP | Multiple AI clients share tools or resources | Standard discovery and interoperability | Adds protocol and security complexity |

Use a REST API for a first-party order or returns service when the consumer and
contract are known. Consider MCP when several agents need the same capabilities.

## Selection Rule

For every use case, record quality, latency, cost, maintainability, governance,
assumptions, rejected alternatives, and the trigger for revisiting the choice.



The most important Day 1 lesson is:

Choose the simplest architecture that satisfies the business requirement, and justify the choice using quality, cost, latency, maintainability, and governance.