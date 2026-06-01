"""
Qdrant database client initialization.
Supports both local and cloud instances.
"""
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest_models
from app.config import settings
import logging

logger = logging.getLogger(__name__)

def get_qdrant_client() -> QdrantClient:
    """
    Initializes and returns QdrantClient instance based on settings.
    Handles cloud authentication via api_key if provided.
    """
    try:
        if settings.QDRANT_API_KEY:
            client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY
            )
            logger.info("Connected to Qdrant Cloud successfully.")
        else:
            client = QdrantClient(
                url=settings.QDRANT_URL or "http://localhost:6333"
            )
            logger.info("Connected to Qdrant Local successfully.")
        return client
    except Exception as e:
        logger.error(f"Error initializing Qdrant client: {e}")
        # Fallback to local default
        return QdrantClient("http://localhost:6333")

def init_qdrant_collection() -> None:
    """
    Ensures that the collection exists in Qdrant. Creates it if not.
    """
    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION_NAME or "truck_products"
    vector_size = settings.EMBEDDING_DIMENSION or 1536
    
    try:
        # Check if collection exists
        collections = client.get_collections().collections
        exists = any(c.name == collection_name for c in collections)
        
        if not exists:
            logger.info(f"Collection '{collection_name}' does not exist. Creating it.")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=rest_models.VectorParams(
                    size=vector_size,
                    distance=rest_models.Distance.COSINE
                )
            )
            logger.info(f"Collection '{collection_name}' created successfully.")
        else:
            logger.info(f"Collection '{collection_name}' already exists.")
    except Exception as e:
        logger.error(f"Failed to initialize Qdrant collection: {e}")
