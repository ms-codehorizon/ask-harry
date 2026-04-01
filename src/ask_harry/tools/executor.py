import inspect

from ask_harry.tools.registry import get_tool, TOOLS


def executor_tool(tool_name:str, arguments: dict):
    if tool_name not in TOOLS:
        return f"ERROR: Tool '{tool_name}' does not exist. You MUST use one of: {list(TOOLS.keys())}"

    tool = get_tool(tool_name)
    arguments = arguments or {}

    try:
        signature = inspect.signature(tool.func)
        accepts_var_kwargs = any(
            parameter.kind == inspect.Parameter.VAR_KEYWORD
            for parameter in signature.parameters.values()
        )

        if not accepts_var_kwargs:
            allowed_args = list(signature.parameters.keys())
            unexpected_args = sorted(set(arguments) - set(allowed_args))
            if unexpected_args:
                return (
                    f"ERROR: Tool '{tool_name}' received unexpected arguments: {unexpected_args}. "
                    f"Allowed arguments: {allowed_args}"
                )

        result = tool.func(**arguments)
        return result
    except TypeError as exc:
        return f"ERROR: Tool '{tool_name}' could not run: {exc}"
