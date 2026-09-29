# Day 4 Deliverables and Homework

The instructor's Day 4 work culminates in an operational readiness assessment.
The local runner creates repeatable score files and a clearly labeled
training-only report. Run `python -m day4.lab` from the repository root; see
[the lab guide](../README.md) for the assignments and tests.

## Generated homework outputs

The runner writes these files here by default:

- `in07_checklist_scores.json` — 12 request-path control checks, plus the
	intentionally flawed starter's baseline score and documented defects.
- `in08_security_scores.json` — the instructor's nine security control keys.
- `in09_governance_scores.json` — the instructor's nine governance/operations
	control keys.
- `day4_training_evidence.json` — IN06–IN09 check results and synthetic SLO data.
- `deployment_readiness_assessment.txt` — final 30-point training rubric and
	observed synthetic SLO measurements.
- `deployment_review_notes.md` — risk register, accountable owner roles,
	monitoring gates, rollback conditions, and release prerequisites.

These files are generated from local fixtures; their score is not production
approval. The sample SLO data intentionally includes breaches so the report
demonstrates how to surface them. Do not replace measured failures with defaults.
Use `python -m day4.lab --live` only when you want the additional single
OpenAI-backed example; it does not change the local score evidence.

## Required evidence

1. **IN06 resilience notes and tests** — failure-mode table plus evidence for
	timeout, bounded retry/backoff, validated tool input, fallback, and
	circuit-breaker recovery.
2. **IN07 production-readiness audit** — baseline and revised scores for all 12
	controls, evidence for each score, identified defects, and unresolved gaps.
	The instructor notebook writes `in07_checklist_scores.json` for IN09.
3. **IN08 security assessment** — threat/test matrix covering normal, malicious,
	and PII-bearing examples; observed outcomes; limitations and moderation
	outage behavior. The notebook writes `in08_security_scores.json` for IN09.
4. **IN09 governance/SLO evidence** — lineage fields (with sensitive values
	excluded or hashed), synthetic latency/availability/block-rate results,
	fallback tests, and rate-limit boundary tests.
5. **Final deployment assessment** — retain
	`deployment_readiness_assessment.txt`, verify its input scores, and add a
	concise review note with verdict, blockers, risks, owners, mitigations, and
	monitoring/review actions.

## Report structure

Use this outline for the human-readable review (the notebook-generated report
may be supplemented; do not silently alter its calculated score):

1. **System and scope:** assistant version, environment, date, and what was not
	tested.
2. **Evidence and score:** IN07, IN08, and IN09 component scores; confirm which
	score files were actually loaded.
3. **Critical findings:** exploit/failure scenario, impact, evidence, severity,
	and whether deployment is blocked.
4. **SLOs:** target, measurement window, denominator, observed synthetic result,
	and action on breach. Label simulated data clearly.
5. **Decision and conditions:** deploy / conditional / block, with explicit
	conditions and accountable owners.
6. **Monitoring and rollback:** alert signals, thresholds, escalation, fallback,
	and next review date.

## Homework status and optional extensions

The four instructor notebooks assign work inside the lesson flow but do not
provide a separate formal homework list. The required evidence above maps those
in-notebook assignments; it is not represented as extra homework from the
instructor.

Optional take-home extensions:

- Replace pattern-only prompt-injection checks with a documented policy and
  adversarial regression suite; record false positives and false negatives.
- Make the rate limiter distributed and identity-aware, then test concurrent
  requests and clock/window boundaries.
- Add a live (non-production) trace export that contains no raw prompts or PII;
  verify redaction with automated tests.
- Define a quality SLO and error-budget policy in addition to latency and
  availability; explain how a breach changes release decisions.
- Add fault-injection tests for model, moderation, cache, and tool outages, and
  document fail-open versus fail-closed behavior for each.

## Review rubric

| Area | Evidence of completion |
| --- | --- |
| Reliability | Bounded time/retries, tested fallback and breaker states, validated inputs |
| Production readiness | All 12 checks scored against observable behavior; gaps are honest |
| Security and privacy | Threat matrix, safe logs, explicit authorization boundary, outage behavior |
| Governance and SLOs | Useful lineage, reproducible synthetic measurements, defined SLO actions |
| Final decision | Inputs verified; no critical gap hidden by aggregate score; owners and monitors named |

Never include API keys, real customer content, or raw PII in deliverables. Keep
generated files out of version control unless they contain only approved,
synthetic data.