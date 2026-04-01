# LLM client layer

# llm.py

from ask_harry.config.settings import Config

config = Config()


def _ollama_llm(prompt: str) -> str:
    import ollama

    messages = [{"role": "user", "content": prompt}]

    response = ollama.chat(model=config.llm_model, messages=messages)

    # debug_print(response)
    return response["message"]["content"]


def _openai_llm(prompt: str) -> str: ...


def _ollama_llm_stream(prompt: str):
    import ollama

    messages = [{"role": "user", "content": prompt}]

    # Use stream=True to get a generator
    stream = ollama.chat(model=config.llm_model, messages=messages, stream=True)

    for chunk in stream:
        yield chunk["message"]["content"]


def generate_stream(prompt: str):
    """Switchboard for streaming responses"""
    if config.llm_provider == "ollama":
        return _ollama_llm_stream(prompt)
    # Add openai stream here later if needed
    else:
        raise ValueError(f"Streaming not supported for: {config.llm_provider}")


def generate(prompt: str) -> str:
    """Switchboard for responses"""
    if config.llm_provider == "ollama":
        return _ollama_llm(prompt=prompt)
    elif config.llm_provider == "openai":
        return _openai_llm(prompt=prompt)
    else:
        raise ValueError(f"Unsupported provider: {config.llm_provider}")

def chat_with_tools(messages: list, tools: list = None):
    """
    Handles a conversation that might include tool calls.
    'messages' is a list of dicts: [{'role': 'user', 'content': '...'}]
    'tools' is a list of tool schemas from your registry.
    """
    import ollama

    if config.llm_provider == "ollama":
        response = ollama.chat(
            model=config.llm_model,
            messages=messages,
            tools=tools
        )
        return response["message"]

    raise ValueError(f"Tools not yet supported for: {config.llm_provider}")