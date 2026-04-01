from ask_harry.ai.embeddings import embed
from ask_harry.config.settings import Config
from ask_harry.retrieval import vector_store
from ask_harry.tools.base import Tool

config = Config()
def vector_search_tool_fn(query: str):
        """
        Search the semantic index for code snippets related to a topic.
        Use this as your first step to find which files are relevant.
        """
        # 1. Embed the tool's query (not the whole user question)
        q_emb = embed(query)
        # 2. Search ChromaDB
        chunks = vector_store.search(q_emb)

        # 3. Format for Harry
        context_output = []
        for i, res in enumerate(chunks, 1):
            source = res.get("source", "Unknown")
            text = res.get("text", "")
            context_output.append(f"--- Result {i} from {source} ---\n{text}")

        return "\n\n".join(context_output) if context_output else "No relevant snippets found."


vector_search_tool = Tool(
    name="vector_search_tool",
    description="""
Semantic search across indexed code snippets.
Use when searching by concept rather than exact text.
    """,
    func=vector_search_tool_fn,
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Technical search terms ."
            }
        },
        "required": ["query"],
        "additionalProperties": False,
    })
