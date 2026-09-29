# Day 4 deployment review notes

## Decision

Training rubric score: 30/30. This is an offline exercise result,
not approval to deploy. A production decision remains **NOT ASSESSED** until
real integrations, access policy, reliability behavior, and monitored SLOs are
verified in an approved environment.

## Risk register and accountable roles

| Risk | Severity | Owner role | Required action / exit evidence |
| --- | --- | --- | --- |
| Heuristic injection, moderation, and exfiltration rules may miss attacks or block benign input | High | Product Security | Approve threat model; test adversarial and benign cases; document false positives/negatives and outage policy |
| External model/tool timeouts may leave work running or duplicate non-idempotent actions | High | Application Engineering | Use native client deadlines/cancellation; enforce idempotency for writes; demonstrate fault-injection recovery |
| PII handling and audit retention are only demonstrated with synthetic data | High | Privacy / Data Governance | Approve classification, minimization, retention, access, deletion, and redaction controls; test with approved fixtures |
| SLO results use five synthetic records, not a production measurement window | High | SRE / Service Owner | Define denominator and rolling window; instrument live-approved telemetry; prove alert and error-budget actions |
| Rate limiter is per-process memory and cannot protect a multi-instance service | Medium | Platform Engineering | Select shared atomic storage and identity key; test concurrency, restart, and boundary behavior |
| Training catalog and return policy are fictional | High | Product Owner | Connect an authorized source of truth and validate freshness, citations, and escalation behavior |

## Monitoring and rollback gates

- Alert on P50/P95/P99 above the approved targets (training examples: 800/2,000/4,000 ms), availability below 99.9%, or blocked-request rate above 1%; define the production aggregation window before launch.
- Immediately disable the affected tool path and roll back or route to human support on unauthorized data access, unmasked PII exposure, or unsafe state-changing action.
- Track model/tool/moderation errors, fallback/cache usage, grounding failures, rate-limit events, safety blocks, latency, and cost with privacy-reviewed metadata only.
- Service Owner: assign a named on-call owner before any launch. Review SLO/error-budget burn weekly during rollout and complete a formal review 30 days after launch.

## Release prerequisites

1. Replace all training fixtures with approved integrations and data.
2. Close every critical security/privacy finding; a high aggregate score cannot waive a critical failure.
3. Attach evidence for the controls, measurement window, rollback test, and human escalation route.
4. Record named approvers and the actual review date in the deployment change record.
