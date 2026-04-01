import os
from dataclasses import dataclass
from pathlib import Path
import logging

from dotenv import load_dotenv

def get_project_root() -> Path:
    """Find the directory containing pyproject.toml."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    # Fallback to a safe number if no toml found
    return current.parents[3]

PROJECT_ROOT = get_project_root()
DEFAULT_DB_PATH = str(PROJECT_ROOT / "data" / "chroma_db")
# Load .env file automatically
load_dotenv(PROJECT_ROOT / ".env", override=True)


def _get_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in ("1", "true", "yes", "on")

@dataclass
class Config:
    """
    Central configuration for RAG CLI app.
    Reads from environment variables with sensible defaults.
    """

    # --- App ---
    app_name: str = "ask_harry"
    environment: str = os.getenv("APP_ENV", "dev")

    # --- Model / LLM ---
    llm_provider: str = os.getenv("LLM_PROVIDER", "ollama")
    llm_model: str = os.getenv("LLM_MODEL", "qwen2.5:7b")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", 0.2))

    # --- Embeddings ---
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "ollama")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text:latest")

    # --- Vector DB ---
    vector_db_path: str = os.getenv("VECTOR_DB_PATH", DEFAULT_DB_PATH)
    collection_name: str = os.getenv("COLLECTION_NAME", "ask_harry")

    # --- Chunking ---
    chunk_size: int = int(os.getenv("CHUNK_SIZE", 500))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", 70))
    min_chunk_size: int = int(os.getenv("MIN_CHUNK_SIZE", 50))

    # --- Retrieval ---
    top_k: int = int(os.getenv("TOP_K", 8))

    # --- Logging ---
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # --- Debug ---
    debug: bool = _get_bool("DEBUG", False)

    def __post_init__(self):
        """Basic validation"""
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        if self.top_k <= 0:
            raise ValueError("top_k must be > 0")

    def debug_print(self):
        """Helpful for CLI debugging"""
        logger = logging.getLogger(self.app_name)
        logger.info("=== CONFIG ===")
        for key, value in self.__dict__.items():
            logger.info("%s: %s", key, value)
