from pathlib import Path


PROMPT_DIR = Path(__file__).parent


def load_prompt(template_name: str, **kwargs) -> str:
    """
    Load a prompt file from ask_harry/prompts
    and substitute variables using .format()

    Example:
        load_prompt(
            "decision.txt",
            question="where is auth implemented"
        )
    """

    file_path = PROMPT_DIR / template_name

    if not file_path.exists():
        raise FileNotFoundError(
            f"Prompt not found: {file_path}"
        )

    template = file_path.read_text()

    try:
        return template.format(**kwargs)

    except KeyError as e:
        raise ValueError(
            f"Missing variable {e} in prompt {template_name}"
        )