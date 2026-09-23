# Day 2 Final Decision Matrix and Architecture Comparison

## Technology Selection

| Decision area | Selected approach | Rationale | Alternative |
| --- | --- | --- | --- |
| RAG components | LangChain | Reusable prompts, embeddings, retrievers, and model integrations | Python-only custom integrations deferred |
| Orchestration | LangGraph | Explicit state, sequential nodes, and conditional routing | Plain functions less extensible |
| Application glue | Python | Clear tests, configuration, and adapters | No extra abstraction needed |
| Agent ownership | In-house | Control over grounding, escalation, data, and evaluation | Hosted harness deferred due to lock-in and cost |
| Agent topology | Bounded workflow with router | Lower cost and easier review | Multi-agent coordination deferred |

## Architecture Comparison

| Dimension | Sequential RAG | Router workflow |
| --- | --- | --- |
| Flow | Retrieve, then answer | Classify, then choose a path |
| Best fit | Questions covered by one knowledge source | Requests with distinct destinations |
| Cost | Lower | Slightly higher orchestration cost |
| Failure mode | Weak or missing evidence | Incorrect route or unclear intent |
| Current use | Approved policy answers | Policy answers versus human escalation |

## Decision

Keep sequential RAG as the default policy path. Use the router only when a
request requires a different capability or a human. Do not add multi-agent
coordination until the router has an evaluation set and measurable failure data.

## Review-Ready Rationale

- **Assumption:** approved policy documents are the source of truth.
- **Evidence:** both examples run against the same policy corpus.
- **Risk:** keyword routing can misclassify ambiguous requests.
- **Consequence:** the router is a learning implementation, not a production
	intent classifier.
- **Change trigger:** add a model classifier or specialist only when evaluation
	shows routing errors that business requirements cannot tolerate.