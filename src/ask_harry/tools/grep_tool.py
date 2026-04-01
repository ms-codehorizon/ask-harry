import re
from pathlib import Path

from ask_harry.retrieval import vector_store
from ask_harry.tools.base import Tool

ALLOWED_EXTENSIONS = {".py", ".md", ".toml", ".yaml", ".yml"} # Added config files
EXCLUDED_FILES = {"uv.lock", "package-lock.json", ".gitignore", "LICENSE"}
EXCLUDED_DIRS = {".git", "__pycache__", ".venv", "node_modules", "data", ".pytest_cache"}

def grep_repo_tool_fn(pattern: str, file_pattern: str = "*"):
    """Search for a string or regex across files. Returns filename:line: content."""
    root_path = vector_store.get_repo_root()
    if not root_path:
        return "Error: No repo ingested. Please ingest a repository first."

    root = Path(root_path)
    results = []

    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error:
        return f"Error: '{pattern}' is not a valid regular expression."

    # Use rglob to find all potential files
    for path in root.rglob(file_pattern):
        # 1. Skip if it's a directory
        if not path.is_file():
            continue

        # 2. Skip by extension
        if path.suffix not in ALLOWED_EXTENSIONS:
            continue

        # 3. Skip by specific filename (uv.lock, etc)
        if path.name in EXCLUDED_FILES:
            continue

        # 4. Skip if any part of the path is in EXCLUDED_DIRS
        if any(part in path.parts for part in EXCLUDED_DIRS):
            continue

        try:
            # We use a context manager (with) to safely open files
            with path.open(encoding="utf-8", errors="ignore") as f:
                for i, line in enumerate(f, 1):
                    if regex.search(line):
                        rel_path = path.relative_to(root)
                        results.append(f"{rel_path}:{i}: {line.strip()}")

                    # Stop searching THIS file if we hit a limit
                    if len(results) >= 25:
                        break
        except Exception:
            continue

        # Stop the whole TOOL if we have enough results for the LLM
        if len(results) >= 25:
            break

    if not results:
        return f"No matches found for '{pattern}' in the allowed source files."

    return "\n".join(results)

grep_repo_tool = Tool(
    name="grep_repo_tool",
    description="""
Search for exact text or regex in repository files.
Use when user provides a specific identifier.
    """,
    func=grep_repo_tool_fn,
    parameters={
        "type": "object",
        "properties": {
            "pattern": {"type": "string", "description": "The text to search for (e.g. '@router')"},
            "file_pattern": {"type": "string", "description": "Optional glob like '*.py'"}
        },
        "required": ["pattern"],
        "additionalProperties": False,
    })
