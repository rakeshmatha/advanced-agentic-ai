"""CLI: run the Walmart multi-agent retail system.

    source ./activate
    retail_multi_agent                       # demo: router (single) + supervisor (multi)
    retail_multi_agent --chat                # interactive (supervisor by default)
    retail_multi_agent --chat --mode router  # interactive router
    retail_multi_agent router "How much is milk?"
    retail_multi_agent supervisor "Price of milk, is it in stock, and can I return it?"
"""

from __future__ import annotations

import argparse
from time import perf_counter

from day3.lab._display import render_table

from .domains import DOMAINS, DOMAIN_ORDER
from .router_system import run as run_router
from .supervisor_system import run as run_supervisor

ROUTER_DEMO = "What is the return policy for a TV?"
SUPERVISOR_DEMO = "What is the price of milk, is it in stock, and can I return it if unopened?"


def print_architecture() -> None:
    print("=" * 72)
    print("Day 3 retail_multi_agent: Walmart specialists + router/supervisor")
    print("=" * 72)
    print(
        render_table(
            ["Agent", "Integration", "Tool"],
            [[name.capitalize(), DOMAINS[name]["integration"], DOMAINS[name]["tools"][0].name]
             for name in DOMAIN_ORDER],
            center={1},
        )
    )
    print("Router     = classify -> ONE agent (single-domain, lowest cost)")
    print("Supervisor = loop across agents until FINISH -> synthesize (multi-domain)")
    print("-" * 72)


def show_router(question: str) -> None:
    started_at = perf_counter()
    result = run_router(question)
    elapsed = perf_counter() - started_at
    print(f"\n[ROUTER]  route -> {result.get('route', '?').upper()}   ({elapsed:.2f}s)")
    print(f"Q: {question}")
    print(f"A: {result.get('answer', '')}\n")


def show_supervisor(question: str) -> None:
    started_at = perf_counter()
    result = run_supervisor(question)
    elapsed = perf_counter() - started_at
    trail = " -> ".join(item["agent"].upper() for item in result.get("findings", [])) or "(none)"
    print(f"\n[SUPERVISOR]  agents used: {trail}   ({elapsed:.2f}s)")
    print(f"Q: {question}")
    if result.get("findings"):
        print(
            render_table(
                ["Agent", "Integration", "Finding"],
                [
                    [
                        item["agent"].capitalize(),
                        DOMAINS[item["agent"]]["integration"],
                        " ".join(str(item["result"]).split())[:80],
                    ]
                    for item in result["findings"]
                ],
                max_widths=[12, 12, 80],
                center={1},
            )
        )
    print(f"A: {result.get('answer', '')}\n")


def demo() -> None:
    print_architecture()
    print("\n### Single-domain question through the ROUTER")
    show_router(ROUTER_DEMO)
    print("### Multi-domain question through the SUPERVISOR")
    show_supervisor(SUPERVISOR_DEMO)


def chat(mode: str) -> None:
    print_architecture()
    print(f"Interactive mode: {mode.upper()}. Type a question. Commands: /exit quits.")
    if mode == "supervisor":
        print("Tip: ask multi-part questions to see several agents cooperate.")
    print("-" * 72)
    while True:
        try:
            question = input("customer> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question == "/exit":
            break
        if mode == "router":
            show_router(question)
        else:
            show_supervisor(question)


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 3 retail_multi_agent system")
    parser.add_argument(
        "mode",
        nargs="?",
        choices=["router", "supervisor", "demo"],
        default="demo",
        help="router (single), supervisor (multi), or demo (both).",
    )
    parser.add_argument("question", nargs="*", help="question to run in the chosen mode")
    parser.add_argument("--chat", action="store_true", help="interactive chat")
    parser.add_argument(
        "--mode",
        dest="chat_mode",
        choices=["router", "supervisor"],
        default="supervisor",
        help="orchestrator for --chat (default: supervisor)",
    )
    args = parser.parse_args()

    if args.chat:
        chat(args.chat_mode)
        return

    question = " ".join(args.question).strip()
    if args.mode == "demo" or not question:
        demo()
    elif args.mode == "router":
        show_router(question)
    else:
        show_supervisor(question)


if __name__ == "__main__":
    main()
