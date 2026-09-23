# Sequential vs Router Comparison

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