"""Day 1 Part 2: Prompt Engineering (matches the instructor notebook).

Runs the same five patterns as
`Walmart-USA-.../Day1/01_LLM_Mechanics_and_Prompt_Engineering.ipynb` Part 2:
zero-shot, few-shot, chain-of-thought, role prompting, and structured output.

Uses the plain OpenAI SDK (no LangChain/LangGraph), exactly like the class.

    source ./activate
    python -m day1.lab.prompts
"""

from __future__ import annotations

import argparse
import json

from pydantic import BaseModel, Field

from common.client import build_client


# --- 2.5 schema for structured output -------------------------------------
class SeverityLevel(str):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ShipmentIncidentReport(BaseModel):
    incident_id: str = Field(description="Generate a short unique ID like INC-001")
    sku: str | None = Field(default=None, description="Product SKU if mentioned, else null")
    incident_type: str = Field(
        description="Category: damaged_goods, delayed_delivery, wrong_item, missing_item, other"
    )
    severity: str = Field(description="One of CRITICAL, HIGH, MEDIUM, LOW")
    financial_impact_usd: float | None = Field(
        default=None, description="Estimated dollar impact if mentioned, else null"
    )
    requires_immediate_action: bool
    recommended_actions: list[str] = Field(description="2-3 concrete next steps")
    summary: str = Field(description="One-sentence summary of the incident")


# --- 2.1 Zero-shot --------------------------------------------------------
def zero_shot_classify(complaint: str) -> str:
    """Classify complaint severity with no examples."""
    client = build_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a Walmart customer support triage system. "
                    "Classify each complaint as CRITICAL, HIGH, MEDIUM, or LOW severity. "
                    "Reply with exactly one word: the severity level."
                ),
            },
            {"role": "user", "content": f"Complaint: {complaint}"},
        ],
        temperature=0,
        max_tokens=10,
    )
    return response.choices[0].message.content.strip()


# --- 2.2 Few-shot ---------------------------------------------------------
def few_shot_extract(feedback: str) -> dict:
    """Extract structured JSON from feedback using few-shot examples."""
    client = build_client()
    prompt = """Extract product information from customer feedback.
Return a JSON object with keys: product_name, sentiment (positive/negative/neutral), issue (or null), rating_implied (1-5).
Return ONLY valid JSON. Do not include markdown or extra text.

Example 1:
Feedback: "The Great Value coffee maker stopped working after 3 weeks. Very disappointing."
Output: {{"product_name": "Great Value coffee maker", "sentiment": "negative", "issue": "stopped working after 3 weeks", "rating_implied": 1}}

Example 2:
Feedback: "Absolutely love my new Onn. TV! Picture quality is stunning and setup was easy."
Output: {{"product_name": "Onn. TV", "sentiment": "positive", "issue": null, "rating_implied": 5}}

Example 3:
Feedback: "The Sam's Choice pasta is decent. Nothing special but good value for the price."
Output: {{"product_name": "Sam's Choice pasta", "sentiment": "neutral", "issue": null, "rating_implied": 3}}

Now extract from:
Feedback: "{feedback}"
Output:"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt.format(feedback=feedback)}],
        response_format={"type": "json_object"},
        temperature=0,
        max_tokens=120,
    )
    return json.loads(response.choices[0].message.content.strip())


# --- 2.3 Chain-of-thought -------------------------------------------------
REORDER_SCENARIO = """
A Walmart distribution center has the following situation:
- Current stock of Product X: 800 units
- Average daily demand: 65 units/day
- Lead time to restock: 8 days
- Safety stock required: 4 days of demand
- Upcoming promotional event in 5 days expected to triple demand for 3 days
"""


def reorder_without_cot() -> str:
    client = build_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": REORDER_SCENARIO + "\nShould we place a reorder today? Answer yes or no."}
        ],
        temperature=0,
        max_tokens=20,
    )
    return response.choices[0].message.content.strip()


def reorder_with_cot() -> str:
    client = build_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": REORDER_SCENARIO
                + "\nShould we place a reorder today? Think step by step, calculate each "
                "quantity explicitly, then give a final recommendation with justification.",
            }
        ],
        temperature=0,
        max_tokens=400,
    )
    return response.choices[0].message.content.strip()


# --- 2.4 Role prompting ---------------------------------------------------
SUPPLIER_PROBLEM = """
Walmart is considering deploying an AI agent to automate supplier negotiation emails.
The agent would draft, send, and respond to routine supplier communications autonomously.
What are the key considerations?
"""

ROLES = {
    "AI Architect": (
        "You are a Senior AI Systems Architect at Walmart Global Tech with 15 years "
        "of experience in enterprise AI deployments. Focus on technical architecture, "
        "reliability, and system design."
    ),
    "Risk Officer": (
        "You are the Chief Risk Officer at a Fortune 500 retailer. Focus on legal "
        "liability, compliance, audit trails, and reputational risk."
    ),
    "Finance Lead": (
        "You are VP of Finance at Walmart. Focus on ROI, cost savings, implementation "
        "costs, and financial governance."
    ),
}


def role_analysis(role_name: str) -> str:
    client = build_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": ROLES[role_name]},
            {"role": "user", "content": SUPPLIER_PROBLEM},
        ],
        temperature=0.2,
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()


# --- 2.5 Structured output ------------------------------------------------
INCIDENT_TEXT = """
Our night shift supervisor just called in. A full pallet of SKU-8832-A (Equate Vitamins, 500 count)
got soaked during the storm because the loading dock door was left open. About 240 units are
completely unsaleable. At $12 retail each, that's roughly $2,880 in damaged inventory.
The supplier needs to be notified and we probably need an emergency restock request since
we're already low on this SKU ahead of the weekend rush.
"""


def parse_incident(incident_text: str = INCIDENT_TEXT) -> ShipmentIncidentReport:
    client = build_client()
    completion = client.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a Walmart operations AI. Extract structured incident information from descriptions.",
            },
            {"role": "user", "content": f"Parse this incident:\n\n{incident_text}"},
        ],
        response_format=ShipmentIncidentReport,
        temperature=0,
    )
    return completion.choices[0].message.parsed


# --- freeform variants for interactive chat -------------------------------
def reason_with_cot(question: str) -> str:
    """Chain-of-thought on any question the user types."""
    client = build_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": question + "\nThink step by step, show your work, then give a final answer.",
            }
        ],
        temperature=0,
        max_tokens=400,
    )
    return response.choices[0].message.content.strip()


def role_answer(role_name: str, problem: str) -> str:
    """Answer any problem in the voice of a chosen role."""
    client = build_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": ROLES[role_name]},
            {"role": "user", "content": problem},
        ],
        temperature=0.2,
        max_tokens=250,
    )
    return response.choices[0].message.content.strip()


def chat_repl() -> None:
    """Pick a prompt pattern, then run it on your own text."""
    patterns = {
        "1": "Zero-shot: classify a complaint's severity",
        "2": "Few-shot: extract JSON from product feedback",
        "3": "Chain-of-thought: reason through a question",
        "4": "Role prompting: answer as a chosen role",
        "5": "Structured output: parse an incident into Pydantic",
    }
    # An example input for each pattern so you know what kind of text to type.
    examples = {
        "1": 'e.g. "I was charged twice and my bank is disputing it."',
        "2": 'e.g. "The Equate tablets work great and cost half the brand name."',
        "3": 'e.g. "Stock 800, demand 65/day, lead 8 days. Reorder today?"',
        "4": 'e.g. "Should we let an AI auto-send supplier emails?"',
        "5": 'e.g. "A pallet of SKU-8832 got soaked; ~240 units ruined, $2,880."',
    }
    print("=" * 70)
    print("Day 1 Prompts: interactive (model: gpt-4o-mini)")
    print("=" * 70)
    print("Each option is a different PROMPTING PATTERN. You pick one, then type")
    print("your own text and see how that pattern shapes the model's answer:")
    print("  1 zero-shot   -> one word, no examples given")
    print("  2 few-shot    -> returns JSON because we showed example JSON")
    print("  3 CoT         -> shows step-by-step reasoning, not just an answer")
    print("  4 role        -> same question, different expert 'voice'")
    print("  5 structured  -> forces a strict Pydantic schema (no loose text)")
    print("Commands: /exit quits.")
    print("-" * 70)
    while True:
        print()
        for key, label in patterns.items():
            print(f"  {key}. {label}  {examples[key]}")
        try:
            choice = input("\npattern> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if choice == "/exit":
            break
        if choice not in patterns:
            print("Pick 1-5 (or /exit).\n")
            continue
        try:
            text = input("your text> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        print()
        if choice == "1":
            print(f"Severity: {zero_shot_classify(text)}")
        elif choice == "2":
            print(json.dumps(few_shot_extract(text), indent=2))
        elif choice == "3":
            print(reason_with_cot(text))
        elif choice == "4":
            role_names = list(ROLES)
            for i, name in enumerate(role_names, 1):
                print(f"  {i}. {name}")
            role_choice = input("role (1-3)> ").strip()
            if role_choice not in {"1", "2", "3"}:
                print("Invalid role.\n")
                continue
            role_name = role_names[int(role_choice) - 1]
            print(f"\n{role_answer(role_name, text)}")
        elif choice == "5":
            report = parse_incident(text)
            print(report.model_dump_json(indent=2))
        print()


def run_demo() -> None:
    print("=== 2.1 Zero-Shot Complaint Classification ===")
    complaints = [
        "My item arrived damaged and I need a replacement immediately.",
        "Website was slow this morning but seems fine now.",
        "I was charged twice for the same order -- my bank is disputing it.",
        "The packaging could be more eco-friendly.",
        "I can't log into my Walmart+ account and my groceries won't deliver.",
    ]
    for complaint in complaints:
        print(f"  {zero_shot_classify(complaint):<10} | {complaint[:55]}")

    print("\n=== 2.2 Few-Shot Structured Extraction ===")
    feedbacks = [
        "The Equate pain relief tablets work great -- I use them every day and they're half the price of brand name.",
        "My Walmart+ order was 2 hours late and the frozen food was partially thawed. Very frustrated.",
        "George men's jeans fit perfectly and the material feels durable. Will buy again.",
    ]
    for feedback in feedbacks:
        print(f"  {few_shot_extract(feedback)}")

    print("\n=== 2.3 Chain-of-Thought Reorder ===")
    print(f"  WITHOUT CoT: {reorder_without_cot()}")
    print("  WITH CoT:")
    print("   " + reorder_with_cot().replace("\n", "\n   "))

    print("\n=== 2.4 Role Prompting ===")
    for role_name in ROLES:
        print(f"\n  --- {role_name} ---")
        print("  " + role_analysis(role_name).replace("\n", "\n  "))

    print("\n=== 2.5 Structured Output (Pydantic) ===")
    report = parse_incident()
    print(f"  Incident ID      : {report.incident_id}")
    print(f"  SKU              : {report.sku}")
    print(f"  Type             : {report.incident_type}")
    print(f"  Severity         : {report.severity}")
    impact = (
        f"${report.financial_impact_usd:,.2f}"
        if report.financial_impact_usd is not None
        else "Not specified"
    )
    print(f"  Financial Impact : {impact}")
    print(f"  Immediate Action : {'YES' if report.requires_immediate_action else 'No'}")
    print(f"  Summary          : {report.summary}")
    print("  Recommended Actions:")
    for i, action in enumerate(report.recommended_actions, 1):
        print(f"    {i}. {action}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 1 prompt engineering lab")
    parser.add_argument("--chat", action="store_true", help="interactive: run a pattern on your own text")
    args = parser.parse_args()
    if args.chat:
        chat_repl()
    else:
        run_demo()


if __name__ == "__main__":
    main()
