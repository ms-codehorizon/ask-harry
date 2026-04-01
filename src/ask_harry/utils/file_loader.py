from pathlib import Path

ALLOWED_EXTENSIONS = {".py", ".md"}

EXCLUDED_DIRS = {".git", "__pycache__", ".venv", "node_modules", "data"}


def load_repo(repo_path: Path):
    files = []

    for path in repo_path.rglob("*"):
        # skip directories
        if not path.is_file():
            continue

        # skip unwanted folders
        if path.suffix not in ALLOWED_EXTENSIONS:
            continue

        if any(part in path.parts for part in EXCLUDED_DIRS):
            continue

        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue

        files.append({"path": str(path), "text": content})

    return files
