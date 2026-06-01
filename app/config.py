"""
Application configurations using Pydantic settings.
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # OpenAI configurations
    OPENAI_API_KEY: str = ""
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"

    # PostgreSQL/SQLite database configuration
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/sales_copilot"

    # Qdrant Vector database configurations
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION_NAME: str = "truck_products"
    EMBEDDING_DIMENSION: int = 1536

    # Neo4j Graph database configurations
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # Retrieval configurations
    VECTOR_TOP_K: int = 5
    GRAPH_TOP_K: int = 5
    TOP_K_HYBRID_RETRIEVER: int = 3

    # Application Port
    PORT: int = 8081

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
