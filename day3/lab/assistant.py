"""Day 3: interactive Walmart Retail Assistant (router orchestration).

Talk to the assistant the way a customer would. It uses the IN05 router pattern
(the recommended production shape): classify the question into PRODUCT / SERVICE
/ ORDER, then answer with that domain's tools.

    source ./activate
    assistant                       # interactive chat
    assistant "Where is my order WM-2024-002?"
"""

from __future__ import annotations

import argparse
from time import perf_counter

from .router import run as run_router
from .tools import TEST_QUERIES

ROUTE_LABEL = {
    "product": "PRODUCT  (search_product, check_inventory)",
    "service": "SERVICE  (get_policy)",
    "order": "ORDER    (get_order_status)",
}


def answer_once(question: str) -> None:
    started_at = perf_counter()
    result = run_router(question)
    elapsed = perf_counter() - started_at
    route = result.get("route", "?")
    print(f"[router -> {ROUTE_LABEL.get(route, route)}]  ({elapsed:.2f}s)")
    print(f"bot> {result.get('answer', '')}\n")


def chat_repl() -> None:
    print("=" * 70)
    print("Day 3 Walmart Retail Assistant  (router orchestration)")
    print("=" * 70)
    print("Ask like a customer. Each turn the assistant:")
    print("  1) classifies your question -> PRODUCT / SERVICE / ORDER")
    print("  2) hands it to that specialist, which calls only its tools")
    print("  3) answers from the tool result")
    print()
    print("Sample data it knows:")
    print("  products: milk, bread, eggs, butter, chicken")
    print("  orders  : WM-2024-001 .. WM-2024-004")
    print("  policies: returns, shipping, price_match, pickup, grocery")
    print()
    print("Try this:")
    for query in TEST_QUERIES[:3]:
        print(f'  "{query}"')
    print()
    print("Commands: /exit quits.")
    print("-" * 70)
    while True:
        try:
            question = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question == "/exit":
            break
        answer_once(question)


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 3 interactive Walmart assistant (router)")
    parser.add_argument("question", nargs="*", help="one-shot question (skip chat)")
    args = parser.parse_args()
    question = " ".join(args.question).strip()
    if question:
        answer_once(question)
    else:
        chat_repl()


if __name__ == "__main__":
    main()
