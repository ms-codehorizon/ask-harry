from pathlib import Path

from ask_harry.retrieval import vector_store
from ask_harry.tools.base import Tool

def read_file_tool_fn(file_path: str):
    """Read the full content of a file from the repository."""
    root = vector_store.get_repo_root()
    if not root:
        return "Error: Repository root not found."

    full_path = Path(root) / file_path

    if not full_path.exists():
        return f"Error: File {file_path} not found. Hint: Use 'list_files_tool' to find the correct relative path."
    try:
        return full_path.read_text(encoding="utf-8")
    except Exception as e:
        return f"Error reading file: {str(e)}"

read_file_tool = Tool(
    name="read_file_tool",
    description="""
Read the full contents of a file.

Use when:
- full function context is needed
- semantic search returns partial snippets
- you need to inspect implementation details
    """,
    func=read_file_tool_fn,
    parameters={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The relative path to the file (e.g., 'src/app.py')"
            }
        },
        "required": ["file_path"],
        "additionalProperties": False,
    })
