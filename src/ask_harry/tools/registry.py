from typing import Dict

from ask_harry.tools.base import Tool

TOOLS: Dict[str, Tool] = {}

def register_tool(tool: Tool):
    TOOLS[tool.name] = tool

def get_tool(tool_name: str):
    if tool_name not in TOOLS:
        raise ValueError(f"tool {tool_name} not registered")
    return TOOLS[tool_name]