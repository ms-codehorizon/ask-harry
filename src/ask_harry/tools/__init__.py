from ask_harry.tools.registry import register_tool


def register_builtin_tools():
    """Register built-in tools lazily to avoid import-time side effects."""
    from ask_harry.tools.grep_tool import grep_repo_tool
    from ask_harry.tools.list_files_tool import list_files_tool
    from ask_harry.tools.read_file_tool import read_file_tool
    from ask_harry.tools.vector_search_tool import vector_search_tool

    for tool in (
        list_files_tool,
        read_file_tool,
        grep_repo_tool,
        vector_search_tool,
    ):
        register_tool(tool)
