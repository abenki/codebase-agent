import os
import json
from agent.tools import tools, execute_tool
from agent.utils import debug_log
from dotenv import load_dotenv

load_dotenv()
MODEL_NAME = os.getenv("MODEL_NAME")

def run_agent(messages, model=MODEL_NAME, client=None, verbose=False):
    """Run the agent loop until the model produces a final answer."""
    if client is None:
        raise ValueError("OpenAI client must be provided.")
    
    if verbose:
        debug_log("STEP 1 — Initial messages", messages)

    while True:
        response = client.chat.completions.create(
            model=model,
            tools=tools,
            messages=messages,
        )

        message = response.choices[0].message
        if verbose:
            debug_log("MODEL RESPONSE", message.model_dump())

        # Execute all tool calls
        if message.tool_calls:
            messages.append(message)
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                if verbose:
                    debug_log(f"EXECUTING TOOL: {tool_name}", args)

                tool_output = execute_tool(tool_name, args)
                if verbose:
                    debug_log(f"TOOL OUTPUT ({tool_name})", tool_output)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_output),
                })

            # Continue looping for possible multi-step tool calls
            continue

        # No more tool calls -> final answer
        if message.content:
            if verbose:
                debug_log("FINAL ANSWER", message.content)
                print("\n✅ FINAL ANSWER:\n" + "-"*80)
            print(message.content)
            messages.append({"role": "assistant", "content": message.content})
            return messages

        # Safety guard
        if response.choices[0].finish_reason == "stop":
            print("Model ended without content.")
            return messages
