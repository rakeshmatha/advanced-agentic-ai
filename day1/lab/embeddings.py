"""Day 1 Part 3: RAG prerequisites -- embeddings basics (matches the notebook).

Mirrors `Walmart-USA-.../Day1/02 RAG Begins/3 RAG_Basic Prerequisites.ipynb`:
turn text of increasing length into embedding vectors and show the vector size.
This is only the RAG *prerequisite*; the full RAG pipeline is Day 2.

    source ./activate
    python -m day1.lab.embeddings
"""

from __future__ import annotations

import argparse
import math

from common.client import build_client

EMBEDDING_MODEL = "text-embedding-3-small"

SAMPLES = [
    "Walmart",
    (
        "Walmart is a multinational retail corporation that operates a chain of "
        "hypermarkets, discount department stores, and grocery stores."
    ),
    (
        "Walmart is a multinational retail corporation that operates a chain of "
        "hypermarkets, discount department stores, and grocery stores. It is one of "
        "the largest companies in the world by revenue and is known for its low prices "
        "and wide selection of products. Walmart was founded by Sam Walton in 1962 and "
        "is headquartered in Bentonville, Arkansas, USA."
    ),
]


def embed(text: str) -> list[float]:
    client = build_client()
    response = client.embeddings.create(model=EMBEDDING_MODEL, input=text)
    return response.data[0].embedding


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """1.0 = identical meaning, ~0 = unrelated."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0


def chat_repl() -> None:
    """Type texts; see each vector and how similar it is to earlier ones."""
    print("=" * 70)
    print(f"Day 1 Embeddings: interactive (model: {EMBEDDING_MODEL})")
    print("=" * 70)
    print("Type any text. It gets turned into a VECTOR (a list of 1536 numbers).")
    print("What you'll see:")
    print("  vector length = always 1536, no matter how long your text is")
    print("  first 5       = a peek at the raw numbers (the 'coordinates')")
    print("  similarity    = cosine score vs each earlier text you typed:")
    print("                  ~1.00 = almost the same meaning")
    print("                  ~0.30 = loosely related")
    print("                  ~0.00 = unrelated")
    print("This is exactly how RAG finds relevant documents (Day 2).")
    print()
    print("Try this to see it work:")
    print('  1) milk      2) dairy      3) lawnmower')
    print("  -> 'milk' vs 'dairy' scores high; 'lawnmower' scores low.")
    print()
    print("Commands: /exit quits.")
    print("-" * 70)
    entries: list[tuple[str, list[float]]] = []
    while True:
        try:
            text = input("text> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if text == "/exit":
            break
        if not text:
            continue
        vector = embed(text)
        preview = ", ".join(f"{value:.4f}" for value in vector[:5])
        print(f"  vector length: {len(vector)} | first 5: [{preview}, ...]")
        if entries:
            print("  similarity to earlier texts:")
            for prev_text, prev_vec in entries:
                score = cosine_similarity(vector, prev_vec)
                print(f"    {score:.4f}  <-  {prev_text[:50]}")
        entries.append((text, vector))
        print()


def run_demo() -> None:
    print(f"Embedding model: {EMBEDDING_MODEL}\n")
    for text in SAMPLES:
        vector = embed(text)
        preview = ", ".join(f"{value:.4f}" for value in vector[:5])
        print(f"Chars: {len(text):>4} | Vector length: {len(vector)} | first 5: [{preview}, ...]")
    print(
        "\nKey insight: every text maps to a fixed-length vector regardless of length. "
        "Similar meaning -> nearby vectors, which is what RAG retrieval uses next (Day 2)."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 1 embeddings lab")
    parser.add_argument("--chat", action="store_true", help="interactive: embed your own text + compare similarity")
    args = parser.parse_args()
    if args.chat:
        chat_repl()
    else:
        run_demo()


if __name__ == "__main__":
    main()
