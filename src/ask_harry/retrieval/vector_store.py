# Interface to the vector database.
# Responsibilities:
#    - Store embeddings
#    - Similarity search
# Goal: Chunks → stored vectors.
# vector_store.py

from pathlib import Path

import chromadb

from ask_harry.config.settings import Config
from ask_harry.utils.utils import logger

config = Config()

persist_directory = config.vector_db_path

client = chromadb.PersistentClient(path=persist_directory)

collection = client.get_or_create_collection(name=config.collection_name)


def store(id, text, embedding, metadata):
    collection.add(ids=[id], documents=[text], embeddings=[embedding], metadatas=[metadata])


def reset_collection():
    """Clear existing data so re-ingesting the same repo does not collide on ids."""
    global collection

    try:
        client.delete_collection(name=config.collection_name)
    except Exception:
        pass

    collection = client.get_or_create_collection(name=config.collection_name)


def search(query_embedding):
    results = collection.query(query_embeddings=[query_embedding], n_results=config.top_k)
    # print(json.dumps(results, indent=4))
    # sources = [m['source'] for m in results['metadatas'][0]]
    # print(json.dumps(sources, indent=4))
    """
    for i in range(len(results['ids'][0])):
        print(f"--- Result {i+1} ---")
        print(f"ID:       {results['ids'][0][i]}")
        print(f"Document: {results['documents'][0][i]}")
        print(f"Metadata: {results['metadatas'][0][i]}")
        print(f"Distance: {results['distances'][0][i]}")
        print("\n")
    """
    # Extract the lists (we use [0] because query_embeddings was a list of one)
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    # Pair them up into a list of results
    context_list = []
    for doc, meta, dist in zip(docs, metas, distances):
        source = meta.get("source", "Unknown source")
        context_list.append(dict(text=doc, source=source, distance=dist))

    return context_list


def is_populated() -> bool:
    # Check if the vector store has been populated
    try:
        count = collection.count()
        if count > 0:
            logger.info(f"Vector store has {count} documents.")
            return True
    except ValueError:
        # get_collection raises ValueError if it doesn't exist
        logger.info("Repository collection not found.")
        return False

    return False


def get_repo_root():
    sample = collection.get(limit=1, include=['metadatas'])

    if sample and sample.get('metadatas') and len(sample['metadatas']) > 0:
        first_metadata_dict = sample['metadatas'][0]
        root = first_metadata_dict.get('repo_root')
        return root

    logger.info("DEBUG: No metadata list found in ChromaDB result!")
    return None

