"""
Init app config
"""

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_EMBEDDING_MODEL: str = os.getenv(
        "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    OPENAI_CHAT_MODEL: str = os.getenv(
        "OPENAI_CHAT_MODEL", "gpt-4o-mini")

    QDRANT_URL: str = os.getenv("QDRANT_URL", "")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "")
    EMBEDDING_DIMENSION: int = os.getenv("EMBEDDING_DIMENSION", 1536)

    NEO4J_URI: str = os.getenv("NEO4J_URI", "")
    NEO4J_USERNAME: str = os.getenv("NEO4J_USERNAME", "")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "")

    VECTOR_TOP_K: int = os.getenv("VECTOR_TOP_K", 5)
    GRAPH_TOP_K: int = os.getenv("GRAPH_TOP_K", 5)
    TOP_K_HYBRID_RETRIEVER: int = os.getenv("TOP_K_HYBRID_RETRIEVER", 5)

    # Set model config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
