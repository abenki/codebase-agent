# Craft Code

A local LLM-powered assistant that can explore, analyze, and modify your codebase through structured tool calls.
Chat with your codebase — locally and privately.

## 🚀 Getting Started
The instructions here are given for using Craft Code with LM Studio running in the background.

1. Set up environment variables
Create a .env variable based on .env.example
- `OPENAI_BASE_URL`: Overrides the default API base URL (`https://api.openai.com/v1`). Use for proxies, Azure OpenAI endpoints, or local compatible APIs (LM Studio for example).
- `OPENAI_API_KEY`: The API Key of your provider if applicable or lm-studio for LM Studio
- `MODEL_NAME`: Name of the LLM to use


2. Clone the repository and install dependencies
```bash
git clone git@github.com:abenki/craft-code.git
cd craft-code
uv sync
```

3. Launch LM Studio, load the model and start the server

4. Run Craft Code
- For a single query:
     ```bash
     uv run src/main.py -q "List all files in the current directory."
     ```
- For interactive mode:
     ```bash
     uv run src/main.py
     ```
     Then type your questions, and Craft Code will respond step-by-step.

Use the `--logs` flag to enable detailed debugging output during execution.

## 🔐 Security & Safety

- All file operations (reading, writing) are sandboxed to prevent unauthorized access.
- The agent enforces path validation to ensure no escape from the `BASE_DIR`.
- Environment variables are loaded from `.env` for secure and consistent configuration.

## 🚧 Agent Limitations

Craft Code has the following limitations:
- The maximum file size that can be read is 20KB.
- The agent cannot perform complex operations, such as refactoring or debugging.

## 🛠️ Supported Tools

The agent can perform the following operations:
- `list_directory`: List files in a directory.
- `read_file`: Read file content (up to 20KB).
- `search_in_file`: Search for text or regex patterns in a file.
- `write_file`: Write or overwrite a file safely.
