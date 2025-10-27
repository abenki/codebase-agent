import os
from agent.utils import safe_path

# Tool definitions
tools = [
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List files in a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to directory"},
                },
                "required": ["path"],
            },
        },
    },
]

def list_directory(path):
    """
    List files in the given directory.
    
    Args:
        path (str): Path to the directory.

    Returns:
        list: List of files in the directory.
    """
    try:
        safe_dir = safe_path(path)
        return os.listdir(safe_dir)
    except Exception as e:
        return {"error": str(e)}

def execute_tool(tool_name, args):
    """Route tool calls to the correct Python function with sandbox enforcement."""
    try:
        if tool_name == "list_directory":
            return list_directory(**args)
        else:
            return {"error": f"Unknown tool '{tool_name}'"}
    except ValueError as e:
        # Catch sandbox violations
        return {"error": str(e)}
