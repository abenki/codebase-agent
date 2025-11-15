import sys
import typer
import tomllib
from openai import OpenAI
from craft_code.core import run_agent
from craft_code.utils import set_base_dir
from craft_code.config.prompts import SYSTEM_PROMPT
from craft_code.config.loader import get_active_model_config, load_config, save_config

app = typer.Typer(
    name="craft-code",
    help="Craft Code. A local LLM-powered assistant that can explore, " \
            "analyze, and modify your codebase through structured tool calls. " \
            "Chat with your codebase — locally and privately."
)

@app.command("configure")
def configure():
    """Interactive configuration wizard for Craft Code."""
    typer.echo("🛠️  Craft Code configuration\n")

    current = load_config()
    provider = typer.prompt(
        "Select provider [lm_studio / ollama / openai]",
        default="lm_studio"
    )

    if provider not in current["models"]:
        typer.echo(f"❌ Unknown provider: {provider}")
        raise typer.Exit(code=1)

    model_cfg = current["models"][provider]
    base_url = typer.prompt("Base URL", default=model_cfg["base_url"])
    model = typer.prompt("Model name", default=model_cfg["model"])

    api_key = model_cfg.get("api_key", "")
    if provider == "openai":
        api_key = typer.prompt("OpenAI API key (starts with sk-...)", default=api_key, hide_input=True)
    elif provider in {"lm_studio", "ollama"}:
        typer.echo("Local mode detected — API key not required.")
        api_key = api_key or provider

    current["provider"] = provider
    current["models"][provider]["base_url"] = base_url
    current["models"][provider]["model"] = model
    current["models"][provider]["api_key"] = api_key

    save_config(current)
    typer.echo("✅ Configuration updated successfully!")

@app.command("ask")
def ask(
    question: str = typer.Argument(..., help="Question to ask Craft Code"),
    logs: bool = typer.Option(False, "--logs", help="Enable debug logs"),
    workspace: str = typer.Option(".", "--workspace", help="Set workspace directory"),
):
    """Ask a single question to Craft Code."""
    cfg = get_active_model_config()
    set_base_dir(workspace)
    client = OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"])

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    run_agent(messages=messages, client=client, verbose=logs)

@app.command("chat")
def chat(
    logs: bool = typer.Option(False, "--logs", help="Enable debug logs"),
    workspace: str = typer.Option(".", "--workspace", help="Set workspace directory"),
):
    """Start an interactive chat session with Craft Code."""
    cfg = get_active_model_config()
    set_base_dir(workspace)
    client = OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"])

    typer.echo("⚒️ Craft Code session started. Type 'exit' or 'quit' to end.\n")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            user_input = typer.prompt("🧑‍💻 You")
        except (EOFError, KeyboardInterrupt):
            typer.echo("\n👋 Session ended.")
            break

        if not user_input.strip():
            # Skip empty lines for better UX
            continue

        if user_input.lower() in {"exit", "quit"}:
            typer.echo("👋 Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})
        messages = run_agent(messages=messages, client=client, verbose=logs)
        typer.echo("") # Add spacing between interactions

@app.command("version")
def version():
    """Display Craft Code version."""
    with open("pyproject.toml", "rb") as f:
        pyproject = tomllib.load(f)
        version = pyproject["project"]["version"]
        typer.echo(f"Craft Code version: {version}")

@app.command("tui")
def tui(
    ctx: typer.Context,
    logs: bool = typer.Option(False, "--logs", help="Enable debug logs"),
    workspace: str = typer.Option(".", "--workspace", help="Set workspace directory"),
):
    """Launch Craft Code TUI (default behavior)."""
    if ctx.invoked_subcommand is None:
        # Launch TUI
        from craft_code.tui.app import CraftCodeApp
        app_instance = CraftCodeApp(workspace=workspace, verbose=logs)
        app_instance.run()

def main():
    if len(sys.argv) == 1:
        sys.argv.append("chat")

    app()

if __name__ == "__main__":
    main()
