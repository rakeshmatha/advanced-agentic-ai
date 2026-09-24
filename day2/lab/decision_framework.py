"""Day 2: Architecture Decision Framework (matches IN01 notebook).

You describe a use case. The model scores it 1-5 on five axes. THIS module's
rules then pick Traditional / Workflow / Hybrid / Agent - the LLM does not
choose the architecture.

    source ./activate
    architecture-decision
    architecture-decision "I need a live chat that answers in under 2 seconds"
    architecture-decision --demo
"""

from __future__ import annotations

import argparse
import textwrap
from typing import TypedDict

from pydantic import BaseModel, Field

from common.client import build_client
from common.config import settings

AXES = [
    "task_complexity",
    "latency_tolerance",
    "cost_ceiling",
    "risk_tolerance",
    "update_frequency",
]

AXIS_LABELS = {
    "task_complexity": "Complexity",
    "latency_tolerance": "Latency",
    "cost_ceiling": "Cost",
    "risk_tolerance": "Risk",
    "update_frequency": "Update freq.",
}

AXIS_SCALE = {
    "task_complexity": "1 = single step  ·  5 = multi-step, dynamic",
    "latency_tolerance": "1 = real-time     ·  5 = batch OK",
    "cost_ceiling": "1 = pennies/query ·  5 = dollars/query",
    "risk_tolerance": "1 = zero errors   ·  5 = caught later",
    "update_frequency": "1 = rarely changes ·  5 = weekly",
}

HYBRID_COMPLEXITY_MIN = 4
HYBRID_CONSTRAINT_MAX = 2

SCORE_SYSTEM = """You are scoring a Walmart software use case on five axes for an architecture decision.
Score each axis 1-5 (integers only). Higher scores push toward agents.
Do NOT recommend an architecture.

For each axis, give 1-3 very short bullet reasons (fragments, not paragraphs).
Each bullet: under 12 words.

Axes:
- task_complexity: 1 = single step / deterministic, 5 = multi-step, dynamic, tool use
- latency_tolerance: 1 = must be real-time (sub-second/seconds), 5 = batch / hours OK
- cost_ceiling: 1 = pennies per query, 5 = dollars per query acceptable
- risk_tolerance: 1 = zero errors allowed, 5 = mistakes can be caught downstream
- update_frequency: 1 = rules rarely change, 5 = weekly changing policy/logic
"""


class Scores(TypedDict):
    task_complexity: int
    latency_tolerance: int
    cost_ceiling: int
    risk_tolerance: int
    update_frequency: int


class Recommendation(TypedDict):
    architecture: str
    total_score: int
    hybrid_override: bool
    rationale: str


class AxisScoreCard(BaseModel):
    task_complexity: int = Field(ge=1, le=5)
    task_complexity_reason: list[str] = Field(min_length=1, max_length=3)
    latency_tolerance: int = Field(ge=1, le=5)
    latency_tolerance_reason: list[str] = Field(min_length=1, max_length=3)
    cost_ceiling: int = Field(ge=1, le=5)
    cost_ceiling_reason: list[str] = Field(min_length=1, max_length=3)
    risk_tolerance: int = Field(ge=1, le=5)
    risk_tolerance_reason: list[str] = Field(min_length=1, max_length=3)
    update_frequency: int = Field(ge=1, le=5)
    update_frequency_reason: list[str] = Field(min_length=1, max_length=3)


def recommend_architecture(scores: Scores) -> Recommendation:
    """IN01 rules. This function is the architecture picker, not the LLM."""
    total = sum(scores[axis] for axis in AXES)
    complexity = scores["task_complexity"]
    latency = scores["latency_tolerance"]
    cost = scores["cost_ceiling"]

    if complexity >= HYBRID_COMPLEXITY_MIN and (
        latency <= HYBRID_CONSTRAINT_MAX or cost <= HYBRID_CONSTRAINT_MAX
    ):
        return {
            "architecture": "Hybrid (Agent + Workflow)",
            "total_score": total,
            "hybrid_override": True,
            "rationale": (
                "High task complexity coexists with a strict latency or cost "
                "constraint. Use a workflow backbone for predictable queries and "
                "invoke a constrained agent only for the complex slice."
            ),
        }

    if total <= 12:
        architecture = "Traditional Software"
        rationale = (
            "Low complexity, strict latency, or a low cost ceiling. A deterministic "
            "pipeline is faster, cheaper, and more predictable than an agent."
        )
    elif total <= 18:
        architecture = "Workflow (Chain)"
        rationale = (
            "Moderate complexity with known steps. A fixed workflow gives LLM "
            "capability without full agent overhead."
        )
    else:
        architecture = "Agent"
        rationale = (
            "High complexity, dynamic branching, or rapidly changing requirements. "
            "An agent is justified if observability and cost controls are in place."
        )
    return {
        "architecture": architecture,
        "total_score": total,
        "hybrid_override": False,
        "rationale": rationale,
    }


USE_CASES: list[dict] = [
    {
        "name": "Automated Returns Processing",
        "scores": {
            "task_complexity": 2,
            "latency_tolerance": 1,
            "cost_ceiling": 1,
            "risk_tolerance": 1,
            "update_frequency": 2,
        },
    },
    {
        "name": "Supplier Risk Intelligence",
        "scores": {
            "task_complexity": 5,
            "latency_tolerance": 4,
            "cost_ceiling": 4,
            "risk_tolerance": 3,
            "update_frequency": 5,
        },
    },
    {
        "name": "Store Performance Analytics Reporter",
        "scores": {
            "task_complexity": 3,
            "latency_tolerance": 5,
            "cost_ceiling": 3,
            "risk_tolerance": 3,
            "update_frequency": 3,
        },
    },
    {
        "name": "Customer Service Live Chat Assistant",
        "scores": {
            "task_complexity": 4,
            "latency_tolerance": 2,
            "cost_ceiling": 2,
            "risk_tolerance": 3,
            "update_frequency": 4,
        },
    },
]


def score_use_case(description: str) -> AxisScoreCard:
    """LLM scores the axes; it does not pick the architecture."""
    client = build_client()
    completion = client.chat.completions.parse(
        model=settings.model,
        messages=[
            {"role": "system", "content": SCORE_SYSTEM},
            {"role": "user", "content": f"Score this use case:\n\n{description}"},
        ],
        response_format=AxisScoreCard,
        temperature=0,
        max_tokens=500,
    )
    parsed = completion.choices[0].message.parsed
    if parsed is None:
        raise ValueError("Model did not return a valid score card.")
    return parsed


def render_table(
    headers: list[str],
    rows: list[list[str]],
    max_widths: list[int | None] | None = None,
    center: set[int] | None = None,
) -> str:
    """Unicode box table with per-column wrapping. No extra dependencies."""
    ncols = len(headers)
    max_widths = max_widths or [None] * ncols
    center = center or set()

    def wrap(text: str, width: int | None) -> list[str]:
        raw_lines = str(text).splitlines() or [""]
        if width is None:
            return raw_lines
        lines: list[str] = []
        for para in raw_lines:
            if para.startswith("• "):
                lines.extend(
                    textwrap.wrap(para, width, subsequent_indent="  ") or ["• "]
                )
            else:
                lines.extend(textwrap.wrap(para, width) or [""])
        return lines or [""]

    wrapped = [[wrap(str(cell), max_widths[i]) for i, cell in enumerate(row)] for row in rows]

    widths = [len(header) for header in headers]
    for cells in wrapped:
        for i, lines in enumerate(cells):
            for line in lines:
                widths[i] = max(widths[i], len(line))

    def pad(text: str, i: int) -> str:
        return text.center(widths[i]) if i in center else text.ljust(widths[i])

    def row_line(cells_line: list[str]) -> str:
        return "│ " + " │ ".join(pad(cells_line[i], i) for i in range(ncols)) + " │"

    bar = lambda l, m, r: l + m.join("─" * (w + 2) for w in widths) + r  # noqa: E731
    out = [bar("┌", "┬", "┐"), row_line(headers), bar("├", "┼", "┤")]
    for idx, cells in enumerate(wrapped):
        if idx:
            out.append(bar("├", "┼", "┤"))
        height = max(len(c) for c in cells)
        for r in range(height):
            out.append(row_line([cells[i][r] if r < len(cells[i]) else "" for i in range(ncols)]))
    out.append(bar("└", "┴", "┘"))
    return "\n".join(out)


def _band(total: int) -> str:
    if total <= 12:
        return "Traditional zone (5-12)"
    if total <= 18:
        return "Workflow zone (13-18)"
    return "Agent zone (19-25)"


def _bullets(items: list[str]) -> str:
    cleaned = []
    for item in items:
        text = item.strip().lstrip("•- ").rstrip(".")
        if text:
            cleaned.append(f"• {text}")
    return "\n".join(cleaned) or "• —"


def decide(description: str) -> None:
    card = score_use_case(description)
    scores: Scores = {axis: getattr(card, axis) for axis in AXES}  # type: ignore[misc]
    result = recommend_architecture(scores)

    print()
    print(f"USE CASE\n  {description}\n")

    print("ASSESSMENT  (scores from the model, 1-5)")
    print(
        render_table(
            ["Axis", "Score", "Scale", "Why this score"],
            [
                [
                    AXIS_LABELS[axis],
                    str(scores[axis]),
                    AXIS_SCALE[axis],
                    _bullets(getattr(card, f"{axis}_reason")),
                ]
                for axis in AXES
            ],
            max_widths=[12, 5, 26, 40],
            center={1},
        )
    )
    print()

    print("DECISION  (chosen by IN01 rules, not the model)")
    print(
        render_table(
            ["Total", "Zone", "Hybrid override", "Architecture"],
            [[
                str(result["total_score"]),
                _band(result["total_score"]),
                "YES" if result["hybrid_override"] else "no",
                result["architecture"],
            ]],
            center={0, 2},
        )
    )
    print()
    print("WHY")
    why_bits = [bit.strip().rstrip(".") for bit in result["rationale"].split(".") if bit.strip()]
    for line in _bullets(why_bits).splitlines():
        print(f"  {line}")
    print()


def print_legend() -> None:
    print("=" * 70)
    print("Day 2 Architecture Decision (IN01)")
    print("=" * 70)
    print("Describe what you want to build. The model scores five axes.")
    print("THIS code then picks the architecture - not the model:")
    print("  Traditional Software | Workflow (Chain) | Hybrid | Agent")
    print()
    print("Bands: 5-12 traditional, 13-18 workflow, 19-25 agent")
    print("Hybrid override: complexity >= 4 AND (latency <= 2 OR cost <= 2)")
    print()
    print("Try this:")
    print('  "Refund unopened returns automatically within 30 days."')
    print('  "Live chat that answers policy questions in under 2 seconds."')
    print('  "Weekly supplier-risk briefing that searches news and scores vendors."')
    print()
    print("Commands: /demo runs the four class examples, /exit quits.")
    print("-" * 70)


def run_demo() -> None:
    print()
    print("DEMO  (four class use cases; architecture chosen by IN01 rules)")
    rows = []
    for use_case in USE_CASES:
        result = recommend_architecture(use_case["scores"])
        rows.append([
            use_case["name"],
            str(result["total_score"]),
            "YES" if result["hybrid_override"] else "no",
            result["architecture"],
            result["rationale"],
        ])
    print(
        render_table(
            ["Use case", "Total", "Override", "Architecture", "Why"],
            rows,
            max_widths=[24, 5, 8, 18, 40],
            center={1, 2},
        )
    )
    print()


def chat_repl() -> None:
    print_legend()
    while True:
        try:
            text = input("use case> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        if text == "/exit":
            break
        if text == "/demo":
            run_demo()
            continue
        decide(text)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Day 2 IN01 architecture decision: describe a use case, get a pick"
    )
    parser.add_argument("--demo", action="store_true", help="score the four class use cases")
    parser.add_argument("use_case", nargs="*", help="one-shot description (skip interactive)")
    args = parser.parse_args()
    description = " ".join(args.use_case).strip()

    if args.demo:
        run_demo()
        return
    if description:
        decide(description)
        return
    chat_repl()


if __name__ == "__main__":
    main()
