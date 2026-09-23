import sys
from time import perf_counter

from day1.lab.app import settings
from day1.lab.app.workflow import answer_question


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        question = input("Ask a customer-service question: ").strip()
    started_at = perf_counter()
    answer, sources = answer_question(question, settings)
    elapsed_seconds = perf_counter() - started_at
    print(f"\nModel: {settings.model}")
    print(f"Time taken: {elapsed_seconds:.2f} seconds")
    print(f"\n{answer}\n")
    print("Sources:")
    for source in sources:
        print(f"- {source}")


if __name__ == "__main__":
    main()