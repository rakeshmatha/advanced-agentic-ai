# Day 4 Practice Lab

Practice the instructor's production-readiness and resilience sequence against
the Walmart retail assistant. The assignments have deterministic local
implementations and real-graph integration tests, plus opt-in OpenAI
model/moderation and guarded Day 3 router/supervisor modes using the shared root
`.env` configuration. Live questions should use synthetic facts; this remains
a training integration, not a production deployment.

## Before you start

1. Review the [Day 4 topics](../topics/README.md).
2. Work through the instructor notebooks in the order listed in
	[the Day 4 guide](../README.md). IN09 consumes score files produced by IN07
	and IN08.
3. Use the repository virtual environment described in the root README. The
	instructor notebooks include OpenAI-backed examples; those require an
	approved `OPENAI_API_KEY` and may incur API usage. Run API calls only when
	authorized. Never paste secrets or real customer data into notebooks,
	outputs, logs, or deliverables.
4. Keep the notebook working directory consistent for the two intermediate
	JSON score files, or copy only non-sensitive score artifacts into the final
	assessment working directory.

## Run the homework

From the repository root, with the project environment active:

```powershell
python -m day4.lab
python -m unittest discover -s day4/lab/tests -v
```

The first command runs repeatable local controls, including the actual Day 3
router and supervisor graphs with fake model decisions, local REST/MCP tools,
and a deterministic policy retriever. It writes IN07/IN08/IN09 scores, evidence,
the report, and review notes to `day4/lab/deliverable/`; no network calls are
made. To send one synthetic-fact example through the OpenAI Responses API and
OpenAI Moderation API, opt in explicitly:

```powershell
python -m day4.lab --live
python -m day4.lab --live --question "What is the sample return policy?"
```

Live mode reads `OPENAI_API_KEY` from the repository-root `.env` using
`common.config` and the existing `common.client`. It does not print the key.
The one model request and input/output moderation requests require network
access and may incur API usage. They do not change the deterministic score files;
those remain based on local test evidence. The instructor notebooks are separate
and may make their own live requests.

To exercise Day 3's real LangGraph across Product REST, Inventory MCP, and
Policy RAG with Day 4 controls around each dependency:

```powershell
python -m day4.lab --multi-agent-live --mode router --question "How much is milk?"
python -m day4.lab --multi-agent-live --mode supervisor --question "What is the price of milk, is it in stock, and what is the return policy?"
```

This mode makes live model calls; the first policy lookup may also make an
embedding API call. The overall deadline defaults to 120 seconds and can be
changed with `--request-timeout`. Local MCP inventory and product/order maps are
fixtures, not Walmart production services. Use synthetic questions only. No
prompts or answers are persisted; request history contains hashed content and
is in-memory for SLO measurements.

## Implementation map

| Module | Assignment implementation |
| --- | --- |
| `resilience.py` | Timeout, bounded retry/backoff, SKU validation, circuit breaker, simulated inventory fallback |
| `security.py` | Injection/jailbreak and exfiltration heuristics, PII masking, local moderation, safe tool-data encoding |
| `live.py` | Opt-in OpenAI Responses API and Moderation API adapters using the shared `.env` client |
| `multi_agent.py` | Day 4 guarded entry point wrapping Day 3's real router/supervisor, per-domain tools, live model calls, lineage, and request SLOs |
| `readiness.py` | Request-path guardrails, grounding, safe audit events, 12 IN07 checks, 9 IN08 checks, 9 IN09 checks |
| `operations.py` | Lineage, routing, streaming demo, fallback chain, SLO measurement, sliding-window limiter |
| `assessment.py` | Score JSON, synthetic evidence, deployment report, and review/risk notes |
| `tests/test_day4.py`, `tests/test_multi_agent.py` | Offline unit and real-graph integration tests |

Timeouts in the demo use a daemon worker; Python cannot forcibly cancel an
arbitrary running thread. Use native client deadlines for real services, and
retry only idempotent operations unless writes have idempotency keys. The local
limiter is process-local. Security rules are deliberately heuristic.

## Assignments

### Assignment 1 — Failure-resilient dependency calls (IN06)

Review and run the notebook-aligned controls around mocked inventory/pricing
dependencies in `resilience.py`:

- Enforce a finite timeout and return a safe, explicit fallback on timeout.
- Retry only retryable failures with bounded exponential backoff; document the
  maximum attempts and delays.
- Validate a model-extracted SKU against trusted known SKUs before lookup.
- Implement and exercise `CLOSED`, `OPEN`, and `HALF-OPEN` circuit-breaker
  transitions, including recovery.

**Acceptance checks:** tests cover fast success, timeout, repeated transient
failure, invalid SKU, open-circuit rejection, and successful half-open recovery.
No test should sleep for long periods or call a live retail service.

### Assignment 2 — Audit and fix production gaps (IN07)

Use the intentionally flawed chatbot and score each of the notebook's 12
checkpoints (0/1) from observed behavior. Identify the eight embedded defects,
review the fixes in `readiness.py`, rerun the same checks, and explain any control
that remains partial or out of scope. The notebook uses score bands of below 8
(block), 8–10 (conditional), and 11+ (approved with monitoring).

**Acceptance checks:** every score has evidence; checks exercise the request
path; rejected input and API failures have defined behavior; logs mask PII; and
the revised score is reproducible. Do not give credit merely because a control
is described in a comment or demonstrated in a disconnected cell.

### Assignment 3 — Layered GenAI security (IN08)

Run the security checks in `security.py` and review the test matrix for prompt
injection/jailbreaks, malicious tool text, invisible characters, PII masking,
exfiltration indicators, and safe audit logging. Include normal input as well as
adversarial test cases to expose false positives.

**Acceptance checks:** demonstrate the security pipeline order; show that the
model is not the authorization boundary; specify what happens if moderation is
unavailable; and ensure raw PII does not enter logs or saved outputs. Document
that heuristic checks cannot guarantee detection.

### Assignment 4 — Governance and operational controls (IN09)

Run `operations.py` to create a safe lineage record; demonstrate simple/complex request routing;
measure synthetic latency/availability/block outcomes; implement primary →
fallback → cache → safe-default degradation; and test the 20-per-60-second
sliding-window session limit.

**Acceptance checks:** record the measurement window and denominator for each
SLO; calculate latency percentiles from synthetic events; test each fallback
stage and rate-limit boundary; and distinguish a synthetic demonstration from
a live-service SLO measurement.

### Assignment 5 — Deployment-readiness review (IN07–IN09)

Run `python -m day4.lab`, verify the generated IN07 and IN08 score files, review
the nine IN09 control results, then read
`day4/lab/deliverable/deployment_readiness_assessment.txt` and
`day4/lab/deliverable/deployment_review_notes.md`. The runner executes all score
checks rather than silently substituting defaults. The instructor notebook's
separate outputs can still use default scores when source files are missing;
verify those inputs if you run the notebook.

**Acceptance checks:** the report identifies its inputs, score and verdict;
records open risks and blockers; names owners/actions for unresolved controls;
and proposes post-deployment monitors, thresholds, and a review date. A high
score does not override a critical security or privacy failure.

## Suggested execution order

```text
IN06 controls → IN07 baseline audit/fixes → IN08 security test matrix
             → IN09 lineage/SLO/fallback/rate limit → final assessment
```

## Submission checklist

The artifact list and report template requirements are in
[lab/deliverable/README.md](deliverable/README.md).