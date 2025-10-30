import argparse
import tomllib
from openai import OpenAI
from agent.core import run_agent
from agent.utils import set_base_dir
from agent.config.prompts import SYSTEM_PROMPT
from agent.config.settings import OPENAI_API_KEY, OPENAI_BASE_URL

def main():
    parser = argparse.ArgumentParser(
        description="Craft Code. A local LLM-powered assistant that can explore, " \
            "analyze, and modify your codebase through structured tool calls. " \
            "Chat with your codebase — locally and privately.")
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
    parser.add_argument(
        "--workspace",
        type=str,
        default=".",
        help="Directory in which Craft Code must operate (defaults to current working directory)."
    )
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="Show Craft Code version."
    )
    args = parser.parse_args()

    if args.version:
        with open("pyproject.toml", "rb") as f:
            pyproject = tomllib.load(f)
            version = pyproject["project"]["version"]
            print(f"Craft Code version: {version}")
        return
    
    set_base_dir(args.workspace)

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
        print("⚒️ Craft Code session started. Type 'exit' or 'quit' to end.\n")
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
