# Ask-Harry Architecture

```mermaid
flowchart TD
    U["User"] --> CLI["CLI Commands<br/>ask | chat | agent | agent-chat | ingest"]

    CLI --> ROUTER{"Route Query?"}
    ROUTER -->|DIRECT| DIRECT["Direct LLM Response"]
    ROUTER -->|REPOSITORY| RAG["RAG / Agent Pipeline"]

    DIRECT --> LLM["LLM Client<br/>Ollama chat/generate"]

    CLI -->|ingest| INGEST["Ingest Service"]
    INGEST --> LOADER["Repository Loader"]
    LOADER --> CHUNKER["Chunker"]
    CHUNKER --> EMBED["Embedding Client"]
    EMBED --> VECTORDB["Chroma Vector Store"]

    RAG --> MODE{"Interaction Mode"}
    MODE -->|ask / chat| SIMPLE["Simple RAG"]
    MODE -->|agent / agent-chat| AGENT["Tool-Using Agent"]

    SIMPLE --> EMBEDQ["Embed User Query"]
    EMBEDQ --> SEARCH["Vector Search"]
    SEARCH --> PROMPT["Prompt Builder"]
    PROMPT --> LLM
    LLM --> RESPONSE["Answer + Citations"]

    AGENT --> AGENTLLM["LLM Tool Planner"]
    AGENTLLM --> TOOLS["Tool Registry / Executor"]
    TOOLS --> VF["vector_search_tool"]
    TOOLS --> GF["grep_repo_tool"]
    TOOLS --> RF["read_file_tool"]
    TOOLS --> LF["list_files_tool"]

    VF --> VECTORDB
    GF --> REPO["Local Repository Files"]
    RF --> REPO
    LF --> REPO

    TOOLS --> AGENTLLM
    AGENTLLM --> FINAL["Grounded Final Answer"]
```

## Notes

- `ingest` builds the searchable repository index.
- `ask` and `chat` use classic retrieval-augmented generation.
- `agent` and `agent-chat` let the LLM choose tools iteratively before answering.
- Conversational inputs can bypass retrieval and go straight to the LLM.
