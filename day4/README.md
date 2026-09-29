# Day 4: Production Readiness, Security, and Resilience

Day 4 turns the Day 3 Walmart assistant into a system that can be assessed for
safe, reliable production operation. The instructor sequence moves from
individual failure controls, to a production-readiness audit, to GenAI security,
and finally to governance, scaling, SLOs, and a deployment assessment.

**Status:** instructor notebooks reviewed; runnable offline assignments,
acceptance tests, assessment artifacts, and an opt-in OpenAI-backed example are
implemented in this folder. The simulations are learning work—not a
certification that the Day 3 assistant is production-ready.

## Learning outcomes

- Bound failures with timeouts, retries, fallbacks, validation, and circuit
	breakers.
- Audit a chatbot against a 12-control production-readiness checklist, then
	improve and re-score it.
- Apply layered defenses for prompt injection, jailbreaks, PII, and attempted
	data exfiltration; understand why pattern matching is not authorization.
- Record request lineage, route work by complexity, measure SLOs, degrade
	gracefully, and limit request rates.
- Produce an evidence-based deployment-readiness assessment with explicit
	blockers and post-deployment monitoring.

## Instructor notebooks

Work through these in order; IN09 consumes score files produced by IN07 and
IN08.

1. [IN06 — Failure Resilience](../../Walmart-USA-21-22-23-28-29-September-2026/Day4/IN06_Failure_Resilience.ipynb)
2. [IN07 — Production Readiness and Reliability Engineering](../../Walmart-USA-21-22-23-28-29-September-2026/Day4/IN07_Production_Readiness_Reliability_Engineering.ipynb)
3. [IN08 — Security for GenAI Systems](../../Walmart-USA-21-22-23-28-29-September-2026/Day4/IN08_Security_GenAI_Systems.ipynb)
4. [IN09 — Governance, Scaling, SLOs, and Resilience Assessment](../../Walmart-USA-21-22-23-28-29-September-2026/Day4/IN09_Governance_Scaling_SLO_Resilience_Assessment.ipynb)

## Practice path

- [Topics](topics/README.md) explains the concepts, their limits, and how the
	four sessions fit together.
- [Lab assignments](lab/README.md) translates the notebook work into runnable
	tasks and acceptance checks. Run `python -m day4.lab` from the repository root.
- [Deliverables and homework](lab/deliverable/README.md) lists the evidence to
	save, report contents, and optional extensions.

## Order and artifacts

| Session | Main practice | Notebook artifact |
| --- | --- | --- |
| IN06 | Exercise timeout, backoff/fallback, structured-output validation, and circuit-breaker behavior | Demonstrated in the notebook; no separate score file |
| IN07 | Audit and improve the flawed assistant against 12 controls | `in07_checklist_scores.json` |
| IN08 | Exercise layered security and PII safeguards | `in08_security_scores.json` |
| IN09 | Add governance/operations controls and combine the module scores | `deployment_readiness_assessment.txt` |

Run IN07 and IN08 before IN09, in the same working directory if using the
notebook defaults. IN09 can substitute default scores when the earlier files
are missing, so verify the inputs in its output rather than treating a generated
report as proof that every exercise ran.

The local runner executes the checks itself, requires no key in offline mode,
and writes synthetic-only files to `day4/lab/deliverable/`. Pass `--live` for
one Responses API + moderation call, or `--multi-agent-live --mode supervisor`
to exercise the actual Day 3 multi-agent graph with Day 4 controls. Live calls
use the root `.env`, may incur model/embedding usage, and are separate from the
reproducible training score. See the [lab run guide](lab/README.md).

The notebooks contain live API examples. Use only approved credentials and
non-sensitive sample data; never commit `.env`, score files containing sensitive
data, or real customer information.