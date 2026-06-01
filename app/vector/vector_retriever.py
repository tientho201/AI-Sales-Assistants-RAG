"""
Retrieval services for Qdrant Vector Database.
"""
from app.config import settings
from app.vector.qdrant_client import get_qdrant_client
from app.vector.embeddings import embedding_service
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def search_vector_products(query: str, top_k: int = None) -> List[Dict[str, Any]]:
    """
    Searches Qdrant database using semantic query string.
    Generates embedding for query, performs search, and returns list of products.
    """
    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION_NAME or "truck_products"
    limit = top_k or settings.VECTOR_TOP_K or 5
    
    try:
        # Check if collection exists first to prevent crashing on empty database
        collections = client.get_collections().collections
        if not any(c.name == collection_name for c in collections):
            logger.warning(f"Qdrant collection '{collection_name}' does not exist. Returning empty search.")
            return []
            
        # Generate query vector
        query_vector = embedding_service.get_embedding(query)
        
        # Search Qdrant
        results = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            with_payload=True
        )
        
        products = []
        for hit in results:
            product = dict(hit.payload)
            product['score'] = float(hit.score)
            products.append(product)
            
        logger.info(f"Qdrant search found {len(products)} products for query: '{query}'")
        return products
    except Exception as e:
        logger.error(f"Error during Qdrant vector search: {e}")
        return []
