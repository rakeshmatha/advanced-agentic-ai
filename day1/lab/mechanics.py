"""Day 1 Part 1: LLM Mechanics (matches the instructor notebook).

Runs the same demos as
`Walmart-USA-.../Day1/01_LLM_Mechanics_and_Prompt_Engineering.ipynb` Part 1:
tokenization, token cost calculator, context-window memory, and temperature.

Uses the plain OpenAI SDK (no LangChain/LangGraph), exactly like the class.

    source ./activate
    python -m day1.lab.mechanics
"""

from __future__ import annotations

import argparse
import time

import tiktoken

from common.client import build_client

# Pricing per 1M tokens (approximate 2026 values from the class notebook).
PRICING = {
    "gpt-4o-mini": {"input": 0.150, "output": 0.600},
    "gpt-4o": {"input": 2.50, "output": 10.00},
}

# gpt-4o tokenizer (o200k_base) also applies to gpt-4o-mini.
_ENC = tiktoken.encoding_for_model("gpt-4o")


def estimate_cost(text: str, model: str = "gpt-4o-mini", direction: str = "input") -> dict:
    """Estimate token count and API cost for a given text."""
    token_count = len(_ENC.encode(text))
    price_per_million = PRICING.get(model, {}).get(direction, 0)
    cost_usd = (token_count / 1_000_000) * price_per_million
    return {
        "text_chars": len(text),
        "token_count": token_count,
        "chars_per_token": round(len(text) / token_count, 2) if token_count else 0,
        "cost_usd": round(cost_usd, 8),
        "cost_per_1000_calls": round(cost_usd * 1000, 4),
    }


def tokenization_demo() -> None:
    """Show how Walmart text, SKUs, and code are split into tokens."""
    texts = [
        "Walmart",
        "Walmart processes 2.3 million customer transactions per hour.",
        "Supply chain optimization using LangGraph and LLM-as-judge evaluation.",
        "SKU-7829341-B",  # a product identifier -- watch how this splits
        "def run_agent(state: AgentState) -> AgentState:",  # code
    ]
    print("=== 1.1 Tokenization ===")
    print(f"Tokenizer: {_ENC.name}")
    print(f"Vocabulary size: {_ENC.n_vocab:,} tokens\n")
    print(f"{'Text':<55} | {'Tokens':>6} | Token IDs (first 8)")
    print("-" * 90)
    for text in texts:
        token_ids = _ENC.encode(text)
        preview = str(token_ids[:8]) + ("..." if len(token_ids) > 8 else "")
        print(f"{text[:54]:<55} | {len(token_ids):>6} | {preview}")
    print("\nKey insight: 'SKU-7829341-B' splits into multiple tokens.")
    print("Structured identifiers cost more tokens than natural text.\n")


def token_cost_demo() -> None:
    """Compare a verbose vs a concise system prompt and scale the cost."""
    prompts = {
        "Verbose system prompt": (
            "You are an AI assistant working at Walmart. Your job is to help "
            "customer service representatives answer questions. You should always "
            "be helpful, professional, and accurate. You must never make up "
            "information that you do not know. Always be polite and courteous to "
            "customers."
        ),
        "Concise system prompt": (
            "You are a Walmart customer service AI. Be accurate, professional, brief."
        ),
    }
    print("=== 1.1b Token Cost Calculator (gpt-4o-mini, input) ===")
    for name, prompt in prompts.items():
        stats = estimate_cost(prompt, "gpt-4o-mini", "input")
        print(f"\n{name}:")
        print(f"  Characters     : {stats['text_chars']}")
        print(f"  Tokens         : {stats['token_count']}")
        print(f"  Cost/call      : ${stats['cost_usd']:.6f}")
        print(f"  Cost/1000 calls: ${stats['cost_per_1000_calls']}")
    print("\nAt 1M calls/day (Walmart scale), the difference compounds.\n")


def context_window_demo() -> None:
    """Show that the model only 'remembers' the history you pass in."""
    client = build_client()
    print("=== 1.2 Context Window (memory = what you send) ===")

    print("\nWithout context (no message history passed):")
    no_context = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "What inventory threshold did I mention?"}],
        max_tokens=80,
        temperature=0,
    )
    print(f"  Model says: {no_context.choices[0].message.content.strip()}")

    history = [
        {"role": "user", "content": "Our reorder threshold for SKU-7829 is 500 units."},
        {"role": "assistant", "content": "Understood. SKU-7829 reorder threshold is 500 units."},
        {"role": "user", "content": "And for SKU-9102 it's 250 units."},
        {"role": "assistant", "content": "Got it. SKU-9102 reorder threshold is 250 units."},
        {"role": "user", "content": "What inventory threshold did I mention for SKU-7829?"},
    ]
    print("\nWith context (full message history passed):")
    with_context = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=history,
        max_tokens=80,
        temperature=0,
    )
    print(f"  Model says: {with_context.choices[0].message.content.strip()}")

    total = sum(len(_ENC.encode(m["content"])) for m in history)
    print(f"\nContext used: ~{total} tokens")
    print(f"Window capacity: 128,000 tokens")
    print(f"Remaining: {128_000 - total:,} tokens\n")


def temperature_demo() -> None:
    """Same prompt at 0.0 / 0.5 / 1.2 to show randomness."""
    client = build_client()
    prompt = "In one sentence, suggest how Walmart can use AI to improve store checkout speed."
    print("=== 1.3 Temperature ===")
    print(f'Prompt: "{prompt}"\n')
    for temp in (0.0, 0.5, 1.2):
        print(f"Temperature = {temp}:")
        for run in range(1, 4):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=temp,
                max_tokens=60,
            )
            print(f"  Run {run}: {response.choices[0].message.content.strip()}")
            time.sleep(0.3)
        print()
    print("At temp=0.0 the runs match. At temp=1.2 they diverge -- risky in production.")
    print("Rule of thumb: use the lowest temperature that still meets quality.\n")


def chat_repl() -> None:
    """Interactive chat that shows mechanics live: memory + tokens + cost.

    The assistant remembers the conversation (context window), and after every
    turn you see how many tokens went in/out and what it cost.
    """
    client = build_client()
    system = {"role": "system", "content": "You are a concise Walmart assistant."}
    history = [system]
    session_cost = 0.0
    print("=" * 70)
    print("Day 1 Mechanics: interactive chat (model: gpt-4o-mini)")
    print("=" * 70)
    print("Type a prompt and press Enter. The assistant REMEMBERS this whole")
    print("conversation - that memory is the 'context window'.")
    print()
    print("After each reply you'll see a stats line. What it means:")
    print("  tokens in   = every token we SENT (system + full history + your prompt)")
    print("  tokens out  = tokens in the model's REPLY")
    print("  turn $      = cost of just this message (in x $0.15 + out x $0.60 per 1M)")
    print("  session $   = running total for this chat")
    print("Tip: 'tokens in' grows every turn because history keeps piling up.")
    print()
    print("Try this to see memory + cost climb:")
    print('  1) "Our reorder threshold for SKU-7829 is 500 units."')
    print('  2) "What threshold did I mention?"   (it remembers)')
    print('  3) /reset  then ask again            (it forgets -> tokens in drops)')
    print()
    print("Commands: /reset clears memory, /exit quits.")
    print("-" * 70)
    while True:
        try:
            user = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not user:
            continue
        if user == "/exit":
            break
        if user == "/reset":
            history = [system]
            print("(memory cleared)\n")
            continue
        history.append({"role": "user", "content": user})
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=history,
            temperature=0,
            max_tokens=200,
        )
        answer = response.choices[0].message.content.strip()
        history.append({"role": "assistant", "content": answer})
        usage = response.usage
        in_cost = usage.prompt_tokens / 1_000_000 * PRICING["gpt-4o-mini"]["input"]
        out_cost = usage.completion_tokens / 1_000_000 * PRICING["gpt-4o-mini"]["output"]
        turn_cost = in_cost + out_cost
        session_cost += turn_cost
        print(f"bot> {answer}")
        print(
            f"     [tokens in={usage.prompt_tokens} out={usage.completion_tokens} "
            f"| turn ${turn_cost:.6f} | session ${session_cost:.6f}]\n"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 1 LLM mechanics lab")
    parser.add_argument("--chat", action="store_true", help="interactive chat with live token/cost stats")
    parser.add_argument("text", nargs="?", help="tokenize + price this text and exit")
    args = parser.parse_args()

    if args.text:
        stats = estimate_cost(args.text)
        print(f"Text   : {args.text}")
        print(f"Tokens : {stats['token_count']} ({stats['chars_per_token']} chars/token)")
        print(f"Cost   : ${stats['cost_usd']:.8f} input on gpt-4o-mini")
        return
    if args.chat:
        chat_repl()
        return

    tokenization_demo()
    token_cost_demo()
    context_window_demo()
    temperature_demo()


if __name__ == "__main__":
    main()
