import os
from pathlib import Path

from ask_harry.retrieval import vector_store
from ask_harry.tools.base import Tool
from ask_harry.utils.file_loader import load_repo


def list_files_tool_fn(**kwargs):
    """Tool: Returns a list of all files in the repository to understand structure."""
    root_path = vector_store.get_repo_root()
    if not root_path:
        return "Error: No repository root found. Please ingest a repo first."

    files_data = load_repo(Path(root_path))
    relative_paths = [
        str(Path(f["path"]).relative_to(root_path))
        for f in files_data
    ]
    if not relative_paths:
        return "The repository appears to be empty or contains no supported files."

    return "FILES IN REPOSITORY:\n" + "\n".join(relative_paths)

list_files_tool = Tool(
    name="list_files_tool",
    description="""
Return a list of repository files.
Use when user asks about project structure or file locations.
    """,
    func=list_files_tool_fn,
    parameters={
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    })
