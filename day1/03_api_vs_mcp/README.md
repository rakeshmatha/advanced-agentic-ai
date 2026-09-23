# 03: API vs MCP

| Option | Best fit | Strength | Trade-off |
| --- | --- | --- | --- |
| REST API | One application owns a stable service contract | Simple, familiar, easy to secure and monitor | Each integration needs custom tool wiring |
| MCP | Multiple AI clients need a shared tool or resource contract | Standard discovery and interoperability | Adds protocol, server, and security complexity |

## Customer-Service Decision

Use a REST API for a first-party order lookup or returns service when the
consumer and contract are known. Consider MCP when several agents or AI tools
need the same capabilities and standardized discovery is valuable.

## Lab

Map two integrations to REST or MCP. Include data sensitivity, authentication,
ownership, expected consumers, operational cost, and failure handling.