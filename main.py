from mini_agent import chat, settings


def main() -> None:
    print(f"Using model: {settings.model}")
    print("Sending a test prompt to OpenAI...")
    answer = chat("Say hello in exactly 5 words.")
    print(answer)


if __name__ == "__main__":
    main()
