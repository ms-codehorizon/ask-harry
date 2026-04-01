"""
Handles the question answering pipeline.
question
↓
embedding
↓
vector search
↓
build prompt
↓
send to LLM
↓
answer
"""
import os

from ask_harry.ai.llm_client import generate, generate_stream, chat_with_tools
from ask_harry.config.settings import Config
from ask_harry.ai.embeddings import embed
from ask_harry.prompts.loader import load_prompt
from ask_harry.prompts.prompts import (
    build_direct_prompt,
    build_prompt,
    build_routing_prompt,
    build_structured_prompt,
)
from ask_harry.tools import register_builtin_tools
from ask_harry.tools.executor import executor_tool
from ask_harry.tools.registry import TOOLS
from ask_harry.utils.utils import display_tool_call, display_agent_response, logger
from ask_harry.retrieval.vector_store import is_populated, search

config = Config()

NO_ANSWER_PHRASE = "I couldn't find any relevant code in the repository to answer that."
chat_history = []
MAX_AGENT_STEPS = 6


def route_question(question: str) -> str:
    if not question.strip():
        return "DIRECT"

    route = generate(build_routing_prompt(question)).strip().upper()
    if "REPOSITORY" in route:
        return "REPOSITORY"
    if "DIRECT" in route:
        return "DIRECT"

    logger.info("Router returned an unexpected label. Falling back to REPOSITORY.")
    return "REPOSITORY"


def agent_question(question: str):
    global chat_history
    register_builtin_tools()

    if route_question(question) == "DIRECT":
        logger.info("Bypassing agent tools for conversational input.")
        answer_text = generate(build_direct_prompt(question))
        chat_history.append({"role": "user", "content": question})
        chat_history.append({"role": "assistant", "content": answer_text})
        display_agent_response(answer_text)
        return answer_text

    if not is_populated():
        raise RuntimeError("Repository not ingested")

    if not chat_history:
        base_prompt = load_prompt("agent_system.txt")
        # Dynamically add the names to the prompt
        # Get the ACTUAL names from your registry
        available_tool_names = ", ".join([f"'{name}'" for name in TOOLS.keys()])
        tool_docs = "\n\n".join(
            f"{tool.name}:\n{tool.description}"
            for tool in TOOLS.values()
        )
        dynamic_prompt = f"{base_prompt}\n\nAVAILABLE TOOLS: {tool_docs}"
        chat_history.append({"role":"system", "content":dynamic_prompt})

    conversation_history = list(chat_history)
    working_history = conversation_history + [{"role": "user", "content": question}]
    tools_schemas = [t.to_ollama_format() for t in TOOLS.values()]
    step = 0
    previous_calls = set()
    while step < MAX_AGENT_STEPS:
        # 1. Ask harry what to do
        response_msg = chat_with_tools(working_history, tools=tools_schemas)

        # 2. harry what to use tools
        if response_msg.get("tool_calls"):
            # add request to history
            working_history.append(response_msg)

            for call in response_msg["tool_calls"]:
                tool_name = call["function"]["name"]
                tool_arguments = call["function"]["arguments"]
                call_signature = f"{tool_name}:{tool_arguments}"

                if call_signature in previous_calls:
                    fallback = "I couldn't confidently answer because the agent repeated the same tool call."
                    chat_history.append({"role": "user", "content": question})
                    chat_history.append({"role": "assistant", "content": fallback})
                    display_agent_response(fallback)
                    return fallback

                display_tool_call(tool_name, tool_arguments)
                # Run the tool
                result = executor_tool(tool_name, tool_arguments)
                previous_calls.add(call_signature)
                # add result to the history
                formatted_result = f"""
                TOOL RESULT:
                tool_name: {tool_name}
                content:
                {result}
                This information may already contain the answer.
                Only call another tool if more detail is required.
                """.strip()
                working_history.append({"role": "tool", "content": str(formatted_result)})
            step += 1
            # we do not return here, we loop so that harry can see the results
            logger.info("Harry is summarizing the results...")
            continue
        answer_text = (response_msg.get("content") or "").strip()
        if not answer_text:
            working_history.append(
                {
                    "role": "user",
                    "content": "Provide a final answer now using the tool results already gathered. Do not call more tools.",
                }
            )
            logger.info("Agent returned an empty final response. Requesting a final answer.")
            step += 1
            continue

        chat_history.append({"role": "user", "content": question})
        chat_history.append({"role": "assistant", "content": answer_text})
        display_agent_response(answer_text)
        return answer_text

    fallback = "I couldn't produce a reliable final answer after several tool steps."
    chat_history.append({"role": "user", "content": question})
    chat_history.append({"role": "assistant", "content": fallback})
    display_agent_response(fallback)
    return fallback

def ask_question(question: str, structured: bool = False):
    if not structured and route_question(question) == "DIRECT":
        logger.info("Bypassing retrieval for conversational input.")
        return generate(build_direct_prompt(question)), {}

    q_emb = embed(question)

    chunks = search(q_emb)
    chunks = sorted(chunks, key=lambda x: x["distance"])

    # build context
    context_parts, source_id_map = build_context(chunks)
    context = "\n\n".join(context_parts)

    if structured:
        prompt = build_structured_prompt(context, question)
    else:
        prompt = build_prompt(context, question)

    answer = generate(prompt)

    return answer, source_id_map


def chat_bot(question: str):
    if not is_populated():
        raise RuntimeError("Repository not ingested. Run ingestion first.")

    if route_question(question) == "DIRECT":
        logger.info("Bypassing retrieval for conversational input.")
        answer_text = generate(build_direct_prompt(question))

        def single_response():
            yield answer_text

        return single_response(), {}

    # Ask Ollama to fix the query first
    # question = generate(normalize_question(question))
    # debug_print(True,f"Original: {question} -> Fixed: {question}")

    q_emb = embed(question)
    chunks = search(q_emb)
    chunks = sorted(chunks, key=lambda x: x["distance"])
    # build context
    context_parts, source_id_map = build_context(chunks)
    context = "\n\n".join(context_parts)

    prompt = build_prompt(context, question)
    answer = generate_stream(prompt)

    return answer, source_id_map


def build_context(chunks: list) -> tuple[list, dict]:
    context_parts = []
    source_id_map = {}
    for i, chunk in enumerate(chunks, start=1):
        source_id_map[i] = chunk["source"]
        filename = os.path.basename(chunk["source"])
        context_parts.append(f"[ID: {i}]\nSOURCE: {filename}\nCONTENT:\n{chunk['text']}")
    # debug_print(f"Context parts:\n{context_parts}")
    # debug_print(f"Source ID MAP: \n{source_id_map}")
    return context_parts, source_id_map


def clean_query(question: str) -> str:
    return generate(question)

def clear_chat_history():
    chat_history.clear()
