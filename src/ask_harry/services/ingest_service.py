# Pipeline for turning files into embeddings.
# wire everything together.
from pathlib import Path

from ask_harry.retrieval.chunker import chunk_text
from ask_harry.ai.embeddings import embed
from ask_harry.utils.file_loader import load_repo
from ask_harry.utils.utils import logger
from ask_harry.retrieval.vector_store import reset_collection, store


def ingest_repo(path: Path):
    files = load_repo(path)
    repo_overview = build_repo_overview(files)
    # Ensure we have the absolute path
    abs_repo_path = str(path.resolve())
    logger.info(f"Using repository root: {abs_repo_path}")
    reset_collection()
    all_chunks = [{
        "text": repo_overview.strip(),
        "source": "repo_overview",
        "repo_root": abs_repo_path
    }]
    # give repo overview 
    logger.debug(f"Loaded {len(files)} files")
    # Step 1: collect ALL chunks
    for file in files:
        file_chunks = chunk_text(file["text"])

        for chunk in file_chunks:
            enriched_text = build_enriched_text(file, chunk)
            all_chunks.append({
                "text" : enriched_text,
                "source": file.get("path", "unknown"),
                "repo_root": abs_repo_path
            })

    # Step 2: embed + store
    for i, chunk in enumerate(all_chunks):
        emb = embed(chunk["text"])
        logger.debug(f"Storing chunk {i}")
        store(
            id=f"chunk-{i}", text=chunk["text"], embedding=emb, metadata={"source": chunk["source"], "repo_root": chunk["repo_root"]}
        )
    logger.debug(f"Total chunks stored: {len(all_chunks)}")

def build_repo_overview(files):

    file_list = "\n".join(f["path"] for f in files)

    return f"""
REPOSITORY OVERVIEW

This repository contains the following files:

{file_list}
"""

def build_enriched_text(file, chunk):
    file_source = file.get("path", "unknown")
    file_name = Path(file_source).name
    enriched_text = f"""FILE NAME: {file_name}\n\n
FILE PATH : {file_source}\n\n
FILE CONTEXT:\n 
FILE CONTEXT:
This is a source code file from a software repository.
It may contain definitions such as:

- functions
- classes
- interfaces
- routes
- handlers
- configurations
- utilities
- tests
- modules
- business logic
CONTENT: \n{chunk}"""
    
    return enriched_text.strip()
