# Engineering Decisions

Day 1 decision artifacts compare architecture choices using complexity,
maintainability, platform support, cost, and governance. The recommendation is
to use Python for application glue, LangChain for RAG components, and LangGraph
when the workflow needs explicit state or branching.

See [decision-matrix.md](decision-matrix.md) for the initial use-case matrix.