"""CLI for the complete, offline Day 4 homework simulation."""

from __future__ import annotations

import argparse
from pathlib import Path

from .assessment import run_homework


def main() -> int:
    default_output = Path(__file__).parent / "deliverable"
    parser = argparse.ArgumentParser(
        description="Run all Day 4 resilience, security, readiness, and SLO exercises offline."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=default_output,
        help=f"where to write score files and the final report (default: {default_output})",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="also run one OpenAI Responses + moderation demo using the root .env key",
    )
    parser.add_argument(
        "--question",
        default="What is the sample return policy?",
        help="question for an opt-in live demo (sent after PII masking)",
    )
    parser.add_argument(
        "--multi-agent-live",
        action="store_true",
        help="run the real Day 3 four-agent LangGraph behind Day 4 guards (uses model and policy-embedding APIs)",
    )
    parser.add_argument(
        "--mode",
        choices=("router", "supervisor"),
        default="supervisor",
        help="Day 3 orchestrator to use with --multi-agent-live",
    )
    parser.add_argument(
        "--request-timeout",
        type=float,
        default=120.0,
        help="overall Day 3 graph deadline in seconds (default: 120)",
    )
    args = parser.parse_args()

    result = run_homework(args.output_dir)
    print("DAY 4 OFFLINE HOMEWORK RESULTS")
    print("Scores (local training checks; not a production certification):")
    print(f"  IN06 resilience:       {result['in06_score']}/{len(result['in06_checks'])}")
    print(f"  IN07 readiness:        {result['in07_score']}/12")
    print(f"  IN08 security:          {result['in08_score']}/9")
    print(f"  IN09 governance:        {result['in09_score']}/9")
    print(f"  Combined rubric:       {result['total_score']}/30")

    failures = [
        f"{domain}.{name}"
        for domain in ("in06", "in07", "in08", "in09")
        for name, passed in result[f"{domain}_checks"].items()
        if not passed
    ]
    if failures:
        print("\nFailed checks:")
        for failure in failures:
            print(f"  - {failure}")
    else:
        print("\nAll local control checks passed.")

    slo_status = result["slo"]["slo_violations"]
    print("Synthetic SLO status:")
    for metric, measurement in slo_status.items():
        print(f"  {measurement['status']:6} {metric}: {measurement['measured']} (target {measurement['target']})")
    print(f"\nArtifacts written to: {result['output_dir']}")
    print("Review deployment_readiness_assessment.txt; its score is training-only.")
    if args.live:
        try:
            from .live import run_live_example

            live_result = run_live_example(args.question)
        except Exception as error:
            print(f"\nLive example failed ({type(error).__name__}); credentials and response values were not printed.")
            return 1
        print("\nLIVE OPENAI DEMO (one model request; moderation on input and output)")
        print(f"  Status: {live_result['status']}")
        print(f"  Source: {live_result['source']}")
        print(f"  Answer: {live_result['answer']}")
        print("  Only fictional training facts are provided as evidence.")
    if args.multi_agent_live:
        try:
            from .multi_agent import Day4MultiAgentHarness, RequestPrincipal

            harness = Day4MultiAgentHarness(request_timeout_seconds=args.request_timeout)
            multi_result = harness.run(
                args.question,
                principal=RequestPrincipal("local-day4-operator"),
                mode=args.mode,
            )
        except Exception as error:
            print(f"\nMulti-agent live example failed ({type(error).__name__}); credentials and response values were not printed.")
            return 1
        print(f"\nGUARDED DAY 3 MULTI-AGENT ({args.mode})")
        print(f"  Status: {multi_result['status']} ({multi_result['reason'] or 'ok'})")
        print(f"  Route: {multi_result.get('route') or 'supervisor'}")
        if multi_result.get("findings"):
            print("  Agents: " + " -> ".join(item["agent"] for item in multi_result["findings"]))
        print(f"  Answer: {multi_result['answer']}")
        print(f"  Request trace events: {len(multi_result['trace'])}; raw prompts/answers are not persisted.")
    elif args.question != "What is the sample return policy?":
        if not args.live and not args.multi_agent_live:
            parser.error("--question requires --live or --multi-agent-live")
    if args.mode != "supervisor" and not args.multi_agent_live:
        parser.error("--mode requires --multi-agent-live")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
