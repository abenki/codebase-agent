from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Input
from textual.binding import Binding

from craft_code.config.loader import get_active_model_config
from craft_code.utils import set_base_dir, BASE_DIR
from craft_code.tui.widgets import ChatHistory, StatusPanel, LogPanel
from craft_code.core import run_agent
from craft_code.config.prompts import SYSTEM_PROMPT
from openai import OpenAI


class CraftCodeApp(App):
    """Craft Code TUI Application."""

    CSS = """
    Screen {
        layout: horizontal;
    }

    #main-container {
        width: 3fr;
        height: 100%;
        layout: vertical;
    }

    #sidebar {
        width: 1fr;
        height: 100%;
        border-left: solid $primary;
    }

    #chat-container {
        height: 1fr;
        border: solid $primary;
        margin: 1;
    }

    #input-container {
        height: auto;
        margin: 0 1;
    }

    #chat-input {
        width: 100%;
    }

    #status-panel {
        height: 100%;
    }

    #log-panel {
        height: 0;
        display: none;
    }

    #log-panel.visible {
        height: 1fr;
        display: block;
        border: solid $accent;
        margin: 1;
    }

    .user-message {
        color: $success;
        padding: 1;
    }

    .assistant-message {
        color: $text;
        padding: 1;
    }

    .system-message {
        color: $warning;
        padding: 1;
        text-style: italic;
    }

    .tool-message {
        color: $accent;
        padding: 1;
        text-style: dim;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("ctrl+l", "toggle_logs", "Toggle Logs"),
        Binding("ctrl+r", "clear_chat", "Clear Chat"),
    ]

    def __init__(self, workspace: str = ".", verbose: bool = False):
        """Initialize Craft Code TUI.
        
        Args:
            workspace: Working directory path
            verbose: Enable verbose logging
        """
        super().__init__()
        self.workspace = workspace
        self.verbose = verbose
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.client = None
        self.is_processing = False

    def compose(self) -> ComposeResult:
        """Compose the TUI layout."""
        yield Header()
        
        with Horizontal():
            with Vertical(id="main-container"):
                yield ChatHistory(id="chat-container")
                yield LogPanel(id="log-panel")
                with Container(id="input-container"):
                    yield Input(
                        placeholder="Type your message or /exit to quit...",
                        id="chat-input"
                    )
        
            yield StatusPanel(id="sidebar")
        
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the application on mount."""
        set_base_dir(self.workspace)
        
        cfg = get_active_model_config()
        self.client = OpenAI(base_url=cfg["base_url"], api_key=cfg["api_key"])
        
        status_panel = self.query_one("#sidebar", StatusPanel)
        status_panel.update_config(cfg, BASE_DIR)
        
        chat = self.query_one("#chat-container", ChatHistory)
        chat.add_system_message("Craft Code initialized. Ready to assist!")
        
        self.query_one("#chat-input", Input).focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user input submission.
        
        Args:
            event: Input submission event
        """
        if self.is_processing:
            return
            
        user_input = event.value.strip()
        if not user_input:
            return
        
        event.input.value = ""
        
        # Handle commands
        if user_input.startswith("/"):
            await self.handle_command(user_input)
            return
        
        # Process message
        chat = self.query_one("#chat-container", ChatHistory)
        chat.add_user_message(user_input)
        
        self.messages.append({"role": "user", "content": user_input})
        
        self.is_processing = True
        status = self.query_one("#sidebar", StatusPanel)
        status.set_processing(True)
        
        try:
            # Run agent in background
            await self.run_agent_async()
        finally:
            self.is_processing = False
            status.set_processing(False)

    async def run_agent_async(self) -> None:
        """Run the agent loop asynchronously."""
        chat = self.query_one("#chat-container", ChatHistory)
        log_panel = self.query_one("#log-panel", LogPanel)
        
        # Define callback to handle messages from agent
        def message_callback(msg: dict) -> None:
            self.call_from_thread(self.handle_agent_message, msg, chat, log_panel)
        
        # Define worker function that captures the arguments
        def worker_func():
            return run_agent(
                messages=self.messages,
                client=self.client,
                verbose=self.verbose,
                callback=message_callback
            )
        
        # Run agent in worker thread
        worker = self.run_worker(worker_func, thread=True)
        self.messages = await worker.wait()

    def handle_agent_message(self, message: dict, chat: ChatHistory, log_panel: LogPanel) -> None:
        """Handle messages from the agent.
        
        Args:
            message: Message dictionary
            chat: ChatHistory widget
            log_panel: LogPanel widget
        """
        if message.get("role") == "assistant":
            content = message.get("content", "")
            if content:
                chat.add_assistant_message(content)
        
        elif message.get("role") == "tool":
            tool_name = message.get("tool_name", "unknown")
            content = message.get("content", "")
            if self.verbose:
                chat.add_tool_message(tool_name, content)
            log_panel.add_log(f"Tool {tool_name}: {content}")
        
        # Log all messages to log panel
        log_panel.add_log(f"Message: {message}")

    async def handle_command(self, command: str) -> None:
        """Handle slash commands.
        
        Args:
            command: Command string starting with /
        """
        chat = self.query_one("#chat-container", ChatHistory)
        
        cmd = command.lower().strip()
        
        if cmd == "/exit" or cmd == "/quit":
            self.exit()
        elif cmd == "/clear":
            self.action_clear_chat()
        elif cmd == "/help":
            help_text = """
Available commands:
- /exit, /quit: Exit Craft Code
- /clear: Clear chat history
- /help: Show this help message
- /logs: Toggle log panel
            """
            chat.add_system_message(help_text.strip())
        elif cmd == "/logs":
            self.action_toggle_logs()
        else:
            chat.add_system_message(f"Unknown command: {command}")

    def action_toggle_logs(self) -> None:
        """Toggle the log panel visibility."""
        log_panel = self.query_one("#log-panel", LogPanel)
        log_panel.toggle_class("visible")

    def action_clear_chat(self) -> None:
        """Clear the chat history."""
        chat = self.query_one("#chat-container", ChatHistory)
        chat.clear()
        self.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        chat.add_system_message("Chat history cleared.")

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
