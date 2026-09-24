"""Day 3: compare the three IN05 orchestration patterns on shared queries.

Runs sequential, router, and supervisor on the same Walmart query set and prints
a boxed summary (route accuracy + latency), matching the IN05 objective to
"measure and compare latency, tool-call count, and routing accuracy".

    source ./activate
    compare
    compare --pattern router
    compare "Check my order WM-2024-002."
"""

from __future__ import annotations

import argparse
from time import perf_counter
from typing import Callable

from ._display import render_table
from .router import run as run_router
from .sequential import run as run_sequential
from .supervisor import run as run_supervisor
from .tools import EXPECTED_ROUTES, TEST_QUERIES

PATTERNS: dict[str, Callable[[str], dict]] = {
    "sequential": run_sequential,
    "router": run_router,
    "supervisor": run_supervisor,
}


def _short(text: str, width: int = 60) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= width else text[: width - 1] + "…"


def _route_cell(question: str, result: dict) -> str:
    actual = result.get("route") or result.get("intent") or "-"
    expected = EXPECTED_ROUTES.get(question)
    if expected is None:
        return str(actual)
    return f"{actual} ✓" if actual == expected else f"{actual} (want {expected})"


def run_pattern(pattern: str, questions: list[str]) -> None:
    runner = PATTERNS[pattern]
    rows = []
    for question in questions:
        started_at = perf_counter()
        result = runner(question)
        elapsed = perf_counter() - started_at
        rows.append([
            _short(question, 46),
            _route_cell(question, result),
            f"{elapsed:.2f}s",
            _short(result.get("answer", ""), 60),
        ])
    print(f"\n{pattern.upper()}")
    print(
        render_table(
            ["Query", "Route", "Latency", "Answer"],
            rows,
            max_widths=[46, 16, 8, 60],
            center={2},
        )
    )


def run_all(questions: list[str]) -> None:
    """One row per query, one column per pattern (route + latency)."""
    timings: dict[str, list[float]] = {p: [] for p in PATTERNS}
    rows = []
    for question in questions:
        row = [_short(question, 42)]
        for pattern, runner in PATTERNS.items():
            started_at = perf_counter()
            result = runner(question)
            elapsed = perf_counter() - started_at
            timings[pattern].append(elapsed)
            row.append(f"{_route_cell(question, result)}\n{elapsed:.2f}s")
        rows.append(row)

    avg_row = ["AVERAGE LATENCY"]
    for pattern in PATTERNS:
        times = timings[pattern]
        avg_row.append(f"{sum(times) / len(times):.2f}s" if times else "-")
    rows.append(avg_row)

    print("\nORCHESTRATION COMPARISON (route + latency per pattern)")
    print(
        render_table(
            ["Query", "Sequential", "Router", "Supervisor"],
            rows,
            max_widths=[42, 18, 18, 18],
        )
    )
    print("\n✓ = router intent matched the expected route for that query.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare Day 3 orchestration patterns on shared queries."
    )
    parser.add_argument(
        "--pattern",
        choices=[*PATTERNS, "all"],
        default="all",
        help="Which pattern to run. Default compares all three.",
    )
    parser.add_argument("question", nargs="*", help="one-shot query (default: shared set)")
    args = parser.parse_args()

    question = " ".join(args.question).strip()
    questions = [question] if question else TEST_QUERIES

    if args.pattern == "all":
        run_all(questions)
    else:
        run_pattern(args.pattern, questions)


if __name__ == "__main__":
    main()
