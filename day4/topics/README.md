# Day 4 Topics: Production Readiness, Security, and Resilience

Day 4 extends the agent and tool systems from Day 3 with operational controls.
The order matters: first contain component failures, then audit the application,
add security defenses, and finally combine governance and SLO evidence into a
deployment decision.

## 1. Failure resilience (IN06)

- **Timeouts:** put a time budget around a slow dependency; define what the
	caller receives when the budget expires.
- **Retries and backoff:** retry transient failures with increasing delays;
	avoid retrying indefinitely or multiplying load during an outage. Jitter can
	reduce synchronized retry bursts.
- **Fallbacks:** use a cached or clearly limited response when a dependency is
	unavailable, and state when data may be stale.
- **Validation before action:** validate structured model output (for example,
	an extracted SKU) against trusted application data before using it in a tool
	call.
- **Circuit breakers:** model `CLOSED`, `OPEN`, and `HALF-OPEN` states so a
	failing service can recover without receiving repeated calls.

The notebook uses simulated slow/flaky APIs for these demonstrations. A timeout
or regex check is a control example, not a complete production resilience
library.

Runnable practice: `day4/lab/resilience.py`; tests cover retry, timeout, invalid
SKU, fallback, and breaker recovery.

## 2. Production-readiness audit (IN07)

The notebook's 12 binary checks cover input validation, prompt-injection
detection, prompt/architecture leakage, deterministic temperature, output
guardrails, grounding, structured audit logging, fallback, SLA timeout,
moderation of input and output, PII masking before logs, and per-user/session
rate limiting. Its score bands are: below 8, block; 8–10, conditional approval;
11 or more, approval with monitoring.

Score controls based on behavior actually exercised—not a comment, configuration
label, or separate demonstration. In particular, distinguish a control that is
implemented, one that is wired into the request path, and one that is tested.
Review the notebook's assembled “fixed” assistant critically: some checklist
items are demonstrated separately or are marked as passing without being
enforced in that path. Record those gaps instead of copying the score blindly.

Runnable practice: `day4/lab/readiness.py` assembles the controls in one request
path and derives its score from local behavior checks.

## 3. Security for GenAI systems (IN08)

- **Threats:** direct and indirect prompt injection, jailbreaks, sensitive-data
	exposure, and exfiltration.
- **Input defenses:** inspect suspicious instruction patterns and invisible or
	control characters; reject, normalize, or route for review according to a
	documented policy.
- **Untrusted tool/retrieval content:** treat it as data, not instructions, and
	keep system policy separate from retrieved text.
- **PII:** detect and mask or hash sensitive values before logs; avoid storing
	raw prompts unless policy and access controls explicitly allow it.
- **Output checks:** check for sensitive data and unsafe responses before
	returning or logging them.
- **Authorization:** enforce access at the application/tool/data boundary.
	Prompt wording, an “exfiltration detector,” and output-size checks do not
	establish user permissions.

The notebook's detectors are heuristic demonstrations. They can miss novel
attacks and can flag benign text. Moderation, regex, and Unicode checks should be
defense-in-depth—not the security boundary. Define fail-closed/fail-open behavior
for a failed moderation service and test that behavior explicitly.

Runnable practice: `day4/lab/security.py` provides local test heuristics;
`day4/lab/live.py` demonstrates opt-in OpenAI moderation with the root `.env`.

## 4. Governance, scaling, and SLOs (IN09)

- **Lineage:** capture model and prompt versions, safe context provenance,
	parameters, latency, and a request identifier. Minimize or hash sensitive
	values; lineage is not a reason to log raw PII.
- **Routing and streaming:** route simple versus complex requests with explicit
	quality and fallback criteria; streaming improves perceived latency but does
	not itself improve correctness. Batching is discussed, not implemented as a
	full service in the notebook.
- **SLOs and error budgets:** define measurable latency percentiles (P50/P95/P99),
	availability, and policy/quality outcomes. A target without a measurement
	window, denominator, and action on breach is not an operational SLO.
- **Graceful degradation:** try primary model, fallback model, cache, and a
	safe static response; make degraded or stale behavior clear.
- **Rate limiting:** the example uses a sliding window of 20 calls per session
	per 60 seconds. Production controls also need identity, distributed storage,
	concurrency, and abuse considerations.
- **Deployment gate:** IN09 combines IN07 and IN08 scores with its own controls
	into a 30-point report and lists monitoring actions. Its sample SLO calls are
	synthetic; they are not measurements of a live service.

## How the notebooks fit together

| Notebook | Main question | Practice evidence |
| --- | --- | --- |
| IN06 | What happens when a dependency is slow, invalid, or failing? | Resilience behavior and failure-mode notes |
| IN07 | Which production controls are present and effective? | 12-point audit and `in07_checklist_scores.json` |
| IN08 | How are untrusted input, PII, and output risks contained? | Security tests and `in08_security_scores.json` |
| IN09 | Is the combined design ready to deploy, and what must be monitored? | SLO/operations evidence and `deployment_readiness_assessment.txt` |

IN09 expects the IN07 and IN08 score files. If they are absent, the notebook can
use fallback scores; check the loaded values before accepting the final result.
The local runner in `day4/lab/assessment.py` creates the score inputs by running
checks first and does not substitute missing-score defaults.

## Day 3 connection

Apply these controls to the existing tool/agent path: validate before tool use,
bound each external call, record safe trace metadata across routing and tool
calls, authorize each data access independently of the model, and define a
fallback or human escalation for unavailable or unsafe results.