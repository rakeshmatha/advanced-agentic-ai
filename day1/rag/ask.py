import sys

from day1.application import settings
from day1.application.workflow import answer_question


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        question = input("Ask a customer-service question: ").strip()
    answer, sources = answer_question(question, settings)
    print(f"\n{answer}\n")
    print("Sources:")
    for source in sources:
        print(f"- {source}")


if __name__ == "__main__":
    main()