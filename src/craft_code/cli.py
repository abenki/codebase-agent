import argparse
import tomllib
from openai import OpenAI
from craft_code.core import run_agent
from craft_code.utils import set_base_dir
from craft_code.config.prompts import SYSTEM_PROMPT
from craft_code.config.loader import get_active_model_config, load_config, save_config

def configure():
    """Interactive configuration wizard for Craft Code."""
    print("🛠️  Craft Code configuration\n")

    current = load_config()
    provider = input("Select provider [lm_studio / ollama / openai] (default: lm_studio): ").strip() or "lm_studio"

    if provider not in current["models"]:
        print(f"❌ Unknown provider: {provider}")
        return

    model_cfg = current["models"][provider]
    base_url = input(f"Base URL [{model_cfg['base_url']}]: ").strip() or model_cfg["base_url"]
    model = input(f"Model name [{model_cfg['model']}]: ").strip() or model_cfg["model"]

    api_key = model_cfg.get("api_key", "")
    if provider == "openai":
        api_key = input("OpenAI API key (starts with sk-...): ").strip() or api_key
    elif provider in {"lm_studio", "ollama"}:
        print("🔐 Local mode detected — API key not required.")
        api_key = api_key or provider

    current["provider"] = provider
    current["models"][provider]["base_url"] = base_url
    current["models"][provider]["model"] = model
    current["models"][provider]["api_key"] = api_key

    save_config(current)

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
    parser.add_argument(
        "--configure", 
        action="store_true", 
        help="Run interactive configuration wizard."
    )

    args = parser.parse_args()

    if args.configure:
        configure()
        return

    if args.version:
        with open("pyproject.toml", "rb") as f:
            pyproject = tomllib.load(f)
            version = pyproject["project"]["version"]
            print(f"Craft Code version: {version}")
        return
    
    cfg = get_active_model_config()

    set_base_dir(args.workspace)

    client = OpenAI(
        base_url=cfg["base_url"], 
        api_key=cfg["api_key"]
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
