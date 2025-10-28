import argparse
from openai import OpenAI
from agent.core import run_agent

parser = argparse.ArgumentParser(description="Run the Codebase Agent with a user question.")
parser.add_argument(
    "-q", "--question",
    type=str,
    required=True,
    help="The question or instruction to ask the agent."
)
parser.add_argument(
    "--logs",
    action="store_true",
    help="Enable verbose debug logging."
)
args = parser.parse_args()

client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

messages = [
    {"role": "system", "content": "You are an assistant that can make changes to a codebase."},
    {"role": "user", "content": args.question},
]

run_agent(messages=messages, client=client, verbose=args.logs)
