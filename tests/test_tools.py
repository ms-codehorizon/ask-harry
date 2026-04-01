from pathlib import Path
from unittest.mock import patch

from ask_harry.tools.base import Tool
from ask_harry.tools.executor import executor_tool
from ask_harry.tools.list_files_tool import list_files_tool_fn
from ask_harry.tools.read_file_tool import read_file_tool_fn


def test_returns_error_for_unknown_tool():
    result = executor_tool("missing_tool", {})
    assert "does not exist" in result


def test_executes_registered_tool():
    tool = Tool(
        name="echo_tool",
        description="Echo a provided message.",
        func=lambda message: f"echo:{message}",
        parameters={},
    )

    with patch.dict("ask_harry.tools.executor.TOOLS", {"echo_tool": tool}, clear=True):
        result = executor_tool("echo_tool", {"message": "hi"})

    assert result == "echo:hi"


def test_returns_error_for_unexpected_tool_arguments():
    tool = Tool(
        name="echo_tool",
        description="Echo a provided message.",
        func=lambda message: f"echo:{message}",
        parameters={},
    )

    with patch.dict("ask_harry.tools.executor.TOOLS", {"echo_tool": tool}, clear=True):
        result = executor_tool("echo_tool", {"message": "hi", "directory": "src"})

    assert "unexpected arguments" in result
    assert "directory" in result


def test_list_files_tool_returns_relative_paths(tmp_path):
    repo = tmp_path
    (repo / "app.py").write_text("print('ok')", encoding="utf-8")
    (repo / "docs.md").write_text("hello", encoding="utf-8")

    with patch("ask_harry.tools.list_files_tool.vector_store.get_repo_root", return_value=str(tmp_path)):
        result = list_files_tool_fn()

    assert "FILES IN REPOSITORY" in result
    assert "app.py" in result
    assert "docs.md" in result


def test_read_file_tool_reads_relative_file(tmp_path):
    nested = tmp_path / "src"
    nested.mkdir()
    (nested / "main.py").write_text("print('hello')", encoding="utf-8")

    with patch("ask_harry.tools.read_file_tool.vector_store.get_repo_root", return_value=str(tmp_path)):
        result = read_file_tool_fn("src/main.py")

    assert result == "print('hello')"


def test_read_file_tool_reports_missing_file():
    with patch("ask_harry.tools.read_file_tool.vector_store.get_repo_root", return_value="/tmp/repo"):
        result = read_file_tool_fn("missing.py")

    assert "not found" in result
