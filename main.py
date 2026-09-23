import sys

from mini_agent import settings
from mini_agent.workflow import answer_question


def main() -> None:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        question = input("Ask a question about the documents: ").strip()
    answer, sources = answer_question(question, settings)
    print(f"\n{answer}\n")
    print("Sources:")
    for source in sources:
        print(f"- {source}")


if __name__ == "__main__":
    main()
