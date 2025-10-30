# Craft Code

A local LLM-powered assistant that can explore, analyze, and modify your codebase through structured tool calls.
Chat with your codebase — locally and privately.

## 🚀 Installation
The instructions here are given for using Craft Code with LM Studio running in the background. If you want to use another provider or local LLM, you will need to set up the environment variables (see [Set up environment variables](#️-set-up-environment-variables)).

Prerequisite: you need to have installed [uv](https://docs.astral.sh/uv/#highlights) and [LM Studio](https://lmstudio.ai/) if you want to run Craft-Code without additional configuration.

1. Clone the repository and install Craft Code
```bash
git clone git@github.com:abenki/craft-code.git
cd craft-code
uv tool install .
```

2. Launch LM Studio, load the model you want to use and start the server. By default, the model used is `"qwen/qwen3-4b-2507"`. If you want to change this behavior, please check [Set up environment variables](#️-set-up-environment-variables).

## 🧑‍💻 Usage

### Single query
```bash
craft-code -q "List all files in the current directory."
```

### Interactive mode
```bash
craft-code
```
     
Then type your questions, and Craft Code will respond step-by-step.

### Arguments
- `--logs`: Use this flag to enable detailed debugging output during execution.
- `--workspace`: Use this argument to specify the folder in which Craft Code should operate. By default, Craft Code runs in the current working directory.
- `--question` or `-q`: Use this argument to run Craft Code in single query mode.
- `--version` or `-v`: Shows the installed version of Craft Code.

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

## ⚙️ Set up environment variables
Create a `.env` file based on `.env.example` and modify your variables as you need.
- `OPENAI_BASE_URL`: Overrides the default API base URL (`https://api.openai.com/v1`). Use for proxies, Azure OpenAI endpoints, or local compatible APIs (LM Studio for example). `.env.example` shows the base URL for LM Studio
- `OPENAI_API_KEY`: The API Key of your provider if applicable or lm-studio for LM Studio
- `MODEL_NAME`: Name of the LLM to use. `.env.example` shows the default model used.
