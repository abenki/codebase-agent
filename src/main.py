import argparse
from openai import OpenAI
from agent.core import run_agent

def main():
    parser = argparse.ArgumentParser(description="Run the Codebase Agent.")
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
        base_url="http://localhost:1234/v1",
        api_key="lm-studio"
    )

    messages = [
        {"role": "system", "content": "You are an assistant that can make changes to a codebase."}
    ]

    if args.question:
        # Single-run mode
        messages.append({"role": "user", "content": args.question})
        run_agent(messages=messages, client=client, verbose=args.logs)
    else:
        # Interactive session mode
        print("🧠 Codebase Agent session started. Type 'exit' or 'quit' to end.\n")
        while True:
            try:
                user_input = input("🧑‍💻 You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Session ended.")
                break
            
            if user_input.lower() in {"exit", "quit"}:
                print("👋 Goodbye!")
                break
            

            # Run one reasoning loop
            messages.append({"role": "user", "content": user_input})
            messages = run_agent(messages=messages, client=client, verbose=args.logs)
            print() # Add spacing between interactions

if __name__ == "__main__":
    main()
