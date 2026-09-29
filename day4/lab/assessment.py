"""Run the complete offline Day 4 homework and write its review artifacts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .readiness import (
    FLAWED_ASSISTANT_DEFECTS,
    IN07_CHECK_LABELS,
    IN08_SECURITY_LABELS,
    IN09_GOVERNANCE_LABELS,
    run_governance_checks,
    run_readiness_checks,
    run_security_checks,
)
from .readiness import run_in06_smoke_checks


def _score(checks: dict[str, bool]) -> int:
    return sum(bool(value) for value in checks.values())


def _verdict(total: int) -> str:
    if total >= 26:
        return "APPROVED WITH MONITORING (training score only)"
    if total >= 20:
        return "CONDITIONAL (training score only; remediate failures)"
    return "BLOCKED (training score only; critical gaps remain)"


def _render_domain(title: str, score: int, checks: dict[str, bool], labels: dict[str, str]) -> list[str]:
    lines = [title, "-" * len(title), f"Score: {score} / {len(labels)}", ""]
    for key, label in labels.items():
        lines.append(f"  [{'PASS' if checks.get(key, False) else 'FAIL'}] {label}")
    return lines


def build_assessment_report(
    *,
    in06_checks: dict[str, bool],
    in07_checks: dict[str, bool],
    in08_checks: dict[str, bool],
    in09_checks: dict[str, bool],
    slo: dict[str, Any],
) -> str:
    """Render a transparent report from observed local checks and synthetic SLOs."""
    in07_score = _score(in07_checks)
    in08_score = _score(in08_checks)
    in09_score = _score(in09_checks)
    total = in07_score + in08_score + in09_score
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "DAY 4 HOMEWORK — OFFLINE TRAINING ASSESSMENT",
        "=" * 56,
        "IMPORTANT: This report is generated from local mocks and synthetic data.",
        "It is not a production certification or evidence about a live Walmart system.",
        f"Assessment date: {timestamp}",
        "Scope: IN06 resilience, IN07 readiness controls, IN08 security, IN09 operations.",
        "",
        "IN06 RESILIENCE SMOKE CHECKS",
        "-" * 31,
    ]
    lines.extend(f"  [{'PASS' if passed else 'FAIL'}] {name}" for name, passed in in06_checks.items())
    lines.append("")
    lines.extend(_render_domain("DOMAIN 1: RELIABILITY + OBSERVABILITY (IN07)", in07_score, in07_checks, IN07_CHECK_LABELS))
    lines.append("")
    lines.extend(_render_domain("DOMAIN 2: SECURITY CONTROLS (IN08)", in08_score, in08_checks, IN08_SECURITY_LABELS))
    lines.append("")
    lines.extend(_render_domain("DOMAIN 3: GOVERNANCE + SCALING + RESILIENCE (IN09)", in09_score, in09_checks, IN09_GOVERNANCE_LABELS))
    lines += [
        "",
        "SYNTHETIC SLO MEASUREMENT",
        "-" * 27,
        f"Calls measured: {slo['total_calls']} (synthetic fixture)",
        f"Percentile method: {slo['percentile_method']}",
    ]
    for metric, result in slo["slo_violations"].items():
        lines.append(
            f"  [{result['status']}] {metric}: measured={result['measured']} target={result['target']}"
        )
    lines += [
        "",
        "FINAL TRAINING SCORE",
        "-" * 20,
        f"Score: {total} / 30",
        f"Training rubric result: {_verdict(total)}",
        "Production decision: NOT ASSESSED — live traffic, access controls, deployment,",
        "human escalation, and operational monitoring were not tested by this lab.",
        "",
        "KNOWN LIMITATIONS / FOLLOW-UP",
        "-" * 28,
        "- Prompt-injection, PII, and moderation rules are small heuristic demonstrations.",
        "- Model, cache, inventory, moderation, and SLO observations use local fixtures.",
        "- The timeout uses a daemon worker; Python cannot forcibly cancel arbitrary code.",
        "- The rate limiter is in-memory and process-local, not distributed.",
        "- Validate security controls with approved adversarial tests and human review.",
        "",
        "IN07 INTENTIONALLY FLAWED STARTER — DOCUMENTED DEFECTS",
        "-" * 54,
    ]
    lines.extend(f"- {defect}" for defect in FLAWED_ASSISTANT_DEFECTS)
    lines += [
        "",
        "NEXT ACTIONS",
        "-" * 12,
        "1. Review every FAIL and attach evidence before changing the score.",
        "2. Assign an owner and due date to unresolved security and reliability gaps.",
        "3. Re-run with approved system integrations and a defined SLO window before any deployment decision.",
    ]
    return "\n".join(lines) + "\n"


def build_review_notes(total_score: int) -> str:
    """Provide the operational follow-up that synthetic scoring cannot decide."""
    return f"""# Day 4 deployment review notes

## Decision

Training rubric score: {total_score}/30. This is an offline exercise result,
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
"""


def run_homework(output_dir: str | Path) -> dict[str, Any]:
    """Execute all local assignments and persist IN07/IN08/IN09-compatible files."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    in06_checks = run_in06_smoke_checks()
    in07_checks = run_readiness_checks()
    in08_checks = run_security_checks()
    in09_checks, slo = run_governance_checks()

    in07_failures = [name for name, passed in in07_checks.items() if not passed]
    in07_data = {
        "baseline_score": 0,
        "baseline_max_score": 12,
        "baseline_note": "Intentionally flawed training starter; score from its documented missing controls.",
        "fixed_score": _score(in07_checks),
        "failures": in07_failures,
        "checklist": in07_checks,
        "evidence_scope": "automated local behavior checks with synthetic inputs",
    }
    (destination / "in07_checklist_scores.json").write_text(
        json.dumps(in07_data, indent=2) + "\n", encoding="utf-8"
    )
    (destination / "in08_security_scores.json").write_text(
        json.dumps(in08_checks, indent=2) + "\n", encoding="utf-8"
    )
    (destination / "in09_governance_scores.json").write_text(
        json.dumps(in09_checks, indent=2) + "\n", encoding="utf-8"
    )

    report = build_assessment_report(
        in06_checks=in06_checks,
        in07_checks=in07_checks,
        in08_checks=in08_checks,
        in09_checks=in09_checks,
        slo=slo,
    )
    (destination / "deployment_readiness_assessment.txt").write_text(report, encoding="utf-8")
    (destination / "deployment_review_notes.md").write_text(
        build_review_notes(_score(in07_checks) + _score(in08_checks) + _score(in09_checks)),
        encoding="utf-8",
    )
    evidence = {
        "assessment_scope": "offline training simulation; not production certification",
        "in06": in06_checks,
        "in07": in07_data,
        "in08": in08_checks,
        "in09": in09_checks,
        "synthetic_slo": slo,
    }
    (destination / "day4_training_evidence.json").write_text(
        json.dumps(evidence, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "output_dir": str(destination.resolve()),
        "in06_score": _score(in06_checks),
        "in07_score": _score(in07_checks),
        "in08_score": _score(in08_checks),
        "in09_score": _score(in09_checks),
        "total_score": _score(in07_checks) + _score(in08_checks) + _score(in09_checks),
        "in06_checks": in06_checks,
        "in07_checks": in07_checks,
        "in08_checks": in08_checks,
        "in09_checks": in09_checks,
        "slo": slo,
    }
