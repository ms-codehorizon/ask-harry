# Wrapper around the embedding model.
# Now generate vectors.
from ask_harry.config.settings import Config
from ask_harry.utils.utils import logger

config = Config()


def embed(text):
    import ollama

    response = ollama.embeddings(model=config.embedding_model, prompt=text)
    logger.debug(f"Response : {response}")
    return response["embedding"]
