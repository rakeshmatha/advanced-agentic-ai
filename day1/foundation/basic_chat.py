from mini_agent import chat, settings


def main() -> None:
    print(f"Using model: {settings.model}")
    print(chat("Explain in one sentence what a context window is."))


if __name__ == "__main__":
    main()