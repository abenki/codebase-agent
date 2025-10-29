import argparse
from openai import OpenAI
from agent.core import run_agent
from agent.config.prompts import SYSTEM_PROMPT
from agent.config.settings import MODEL_NAME, OPENAI_API_KEY, OPENAI_BASE_URL

def main():
    parser = argparse.ArgumentParser(description="Run Craft Code.")
    parser.add_argument(
        "-q", "--question",
        type=str,
        help="Ask a single question."
    )
    parser.add_argument(
        "--logs",
        action="store_true",
        help="Show detailed debug logs."
    )
    args = parser.parse_args()

    client = OpenAI(
        base_url=OPENAI_BASE_URL,
        api_key=OPENAI_API_KEY
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

    if args.question:
        # Single-run mode
        messages.append({"role": "user", "content": args.question})
        run_agent(messages=messages, client=client, verbose=args.logs)
    else:
        # Interactive session mode
        print("🧠 Craft Code session started. Type 'exit' or 'quit' to end.\n")
        while True:
            try:
                user_input = input("🧑‍💻 You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Session ended.")
                break

            if not user_input:
                # Skip empty lines for better UX
                continue
            
            if user_input.lower() in {"exit", "quit"}:
                print("👋 Goodbye!")
                break
            

            # Run one reasoning loop
            messages.append({"role": "user", "content": user_input})
            messages = run_agent(messages=messages, client=client, verbose=args.logs)
            print() # Add spacing between interactions

if __name__ == "__main__":
    main()
