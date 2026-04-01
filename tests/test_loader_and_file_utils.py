from pathlib import Path
from unittest.mock import patch

import pytest

from ask_harry.prompts.loader import load_prompt
from ask_harry.utils.file_loader import load_repo


def test_load_prompt_formats_template(tmp_path):
    prompt_dir = tmp_path
    (prompt_dir / "greeting.txt").write_text("Hello {name}!", encoding="utf-8")

    with patch("ask_harry.prompts.loader.PROMPT_DIR", prompt_dir):
        result = load_prompt("greeting.txt", name="Harry")

    assert result == "Hello Harry!"


def test_load_prompt_raises_for_missing_file(tmp_path):
    with patch("ask_harry.prompts.loader.PROMPT_DIR", Path(tmp_path)):
        with pytest.raises(FileNotFoundError):
            load_prompt("missing.txt")


def test_load_prompt_raises_for_missing_variable(tmp_path):
    prompt_dir = tmp_path
    (prompt_dir / "greeting.txt").write_text("Hello {name}!", encoding="utf-8")

    with patch("ask_harry.prompts.loader.PROMPT_DIR", prompt_dir):
        with pytest.raises(ValueError):
            load_prompt("greeting.txt")


def test_load_repo_only_includes_supported_files(tmp_path):
    repo = tmp_path
    (repo / "main.py").write_text("print('ok')", encoding="utf-8")
    (repo / "README.md").write_text("# Title", encoding="utf-8")
    (repo / "notes.txt").write_text("ignore me", encoding="utf-8")
    (repo / ".venv").mkdir()
    (repo / ".venv" / "hidden.py").write_text("print('skip')", encoding="utf-8")
    (repo / "data").mkdir()
    (repo / "data" / "doc.md").write_text("skip", encoding="utf-8")

    files = load_repo(repo)

    loaded_paths = {Path(item["path"]).name for item in files}
    assert loaded_paths == {"main.py", "README.md"}
