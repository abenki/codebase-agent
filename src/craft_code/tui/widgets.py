from textual.widgets import Static, RichLog
from textual.containers import VerticalScroll
from rich.text import Text
from rich.markdown import Markdown
from datetime import datetime


class ChatHistory(VerticalScroll):
    """Widget to display chat history with auto-scroll."""

    def __init__(self, **kwargs):
        """Initialize ChatHistory widget.
        
        Args:
            **kwargs: Additional keyword arguments for VerticalScroll
        """
        super().__init__(**kwargs)
        self.can_focus = False

    def add_user_message(self, content: str) -> None:
        """Add a user message to the chat.
        
        Args:
            content: Message content
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        text = Text()
        text.append(f"[{timestamp}] ", style="dim")
        text.append("You: ", style="bold green")
        text.append(content)
        
        message_widget = Static(text, classes="user-message")
        self.mount(message_widget)
        self.scroll_end(animate=False)

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the chat.
        
        Args:
            content: Message content
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        text = Text()
        text.append(f"[{timestamp}] ", style="dim")
        text.append("Craft Code: ", style="bold cyan")
        text.append("\n")
        
        message_widget = Static(text, classes="assistant-message")
        self.mount(message_widget)
        
        # Render markdown content
        try:
            md = Markdown(content)
            md_widget = Static(md, classes="assistant-message")
            self.mount(md_widget)
        except Exception:
            # Fallback to plain text
            plain_widget = Static(content, classes="assistant-message")
            self.mount(plain_widget)
        
        self.scroll_end(animate=False)

    def add_system_message(self, content: str) -> None:
        """Add a system message to the chat.
        
        Args:
            content: Message content
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        text = Text()
        text.append(f"[{timestamp}] ", style="dim")
        text.append("System: ", style="bold yellow italic")
        text.append(content, style="italic")
        
        message_widget = Static(text, classes="system-message")
        self.mount(message_widget)
        self.scroll_end(animate=False)

    def add_tool_message(self, tool_name: str, content: str) -> None:
        """Add a tool execution message to the chat.
        
        Args:
            tool_name: Name of the tool
            content: Tool output content
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        text = Text()
        text.append(f"[{timestamp}] ", style="dim")
        text.append(f"Tool ({tool_name}): ", style="bold magenta dim")
        text.append(content[:200], style="dim")  # Truncate long outputs
        if len(content) > 200:
            text.append("...", style="dim")
        
        message_widget = Static(text, classes="tool-message")
        self.mount(message_widget)
        self.scroll_end(animate=False)

    def clear(self) -> None:
        """Clear all messages from chat history."""
        for child in list(self.children):
            child.remove()


class StatusPanel(Static):
    """Widget to display current status and configuration."""

    def __init__(self, **kwargs):
        """Initialize StatusPanel widget.
        
        Args:
            **kwargs: Additional keyword arguments for Static
        """
        super().__init__("", **kwargs)
        self.provider = "unknown"
        self.model = "unknown"
        self.workspace = "."
        self.processing = False

    def update_config(self, config: dict, workspace: str) -> None:
        """Update configuration display.
        
        Args:
            config: Configuration dictionary
            workspace: Workspace path
        """
        self.provider = config.get("provider", "unknown")
        self.model = config.get("model", "unknown")
        self.workspace = workspace
        self.refresh_display()

    def set_processing(self, processing: bool) -> None:
        """Set processing status.
        
        Args:
            processing: Whether the agent is processing
        """
        self.processing = processing
        self.refresh_display()

    def refresh_display(self) -> None:
        """Refresh the status display."""
        status_icon = "🔄" if self.processing else "✓"
        status_text = "Processing..." if self.processing else "Ready"
        
        content = Text()
        content.append("Status\n", style="bold underline cyan")
        content.append(f"{status_icon} {status_text}\n\n", style="green" if not self.processing else "yellow")
        
        content.append("Configuration\n", style="bold underline cyan")
        content.append("Provider: ", style="dim")
        content.append(f"{self.provider}\n", style="bold")
        content.append("Model: ", style="dim")
        content.append(f"{self.model}\n\n", style="bold")
        
        content.append("Workspace\n", style="bold underline cyan")
        content.append(f"{self.workspace}\n\n", style="dim")
        
        content.append("Tools\n", style="bold underline cyan")
        tools = [
            "list_directory",
            "read_file",
            "search_in_file",
            "write_file"
        ]
        for tool in tools:
            content.append(f"• {tool}\n", style="dim")
        
        content.append("\n")
        content.append("Shortcuts\n", style="bold underline cyan")
        content.append("Ctrl+C: Quit\n", style="dim")
        content.append("Ctrl+L: Logs\n", style="dim")
        content.append("Ctrl+R: Clear\n", style="dim")
        content.append("\n")
        content.append("/exit: Quit\n", style="dim")
        content.append("/clear: Clear chat\n", style="dim")
        content.append("/help: Show help\n", style="dim")
        
        self.update(content)


class LogPanel(RichLog):
    """Widget to display debug logs."""

    def __init__(self, **kwargs):
        """Initialize LogPanel widget.
        
        Args:
            **kwargs: Additional keyword arguments for RichLog
        """
        super().__init__(**kwargs)
        self.max_lines = 1000

    def add_log(self, message: str) -> None:
        """Add a log entry.
        
        Args:
            message: Log message
        """
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self.write(f"[{timestamp}] {message}")
