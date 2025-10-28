# Codebase Agent

A local LLM-powered assistant that can explore, analyze, and modify your codebase through structured tool calls.
Chat with your codebase — locally and privately.

## 🚀 Getting Started

1. Set up environment variables
Create a .env variable based on .env.example

2. Install dependencies
```bash
uv sync
```

3. **Run the agent**
- For a single query:
     ```bash
     uv run src/main.py -q "List all files in the current directory."
     ```
- For interactive mode:
     ```bash
     uv run src/main.py
     ```
     Then type your questions, and the agent will respond step-by-step.

Use the `--logs` flag to enable detailed debugging output during execution.

## 🔐 Security & Safety

- All file operations (reading, writing) are sandboxed to prevent unauthorized access.
- The agent enforces path validation to ensure no escape from the `BASE_DIR`.
- Environment variables are loaded from `.env` for secure and consistent configuration.

## 🛠️ Supported Tools

The agent can perform the following operations:
- `list_directory`: List files in a directory.
- `read_file`: Read file content (up to 20KB).
- `search_in_file`: Search for text or regex patterns in a file.
- `write_file`: Write or overwrite a file safely.
