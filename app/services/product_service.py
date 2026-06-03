"""
Product service managing CSV ingestion into both Qdrant and Neo4j.
"""
from app.vector.vector_builder import ingest_csv_to_qdrant
from app.vector.qdrant_client import get_qdrant_client
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


def ingest_products_from_csv(csv_path: str) -> Dict[str, Any]:
    """
    Ingests product data from CSV file into Qdrant databases.
    """
    result = {
        "status": "success",
        "qdrant_count": 0,
        "message": ""
    }

    # 1. Ingest to Qdrant Vector DB
    try:
        qdrant_count = ingest_csv_to_qdrant(csv_path)
        result["qdrant_count"] = qdrant_count
        logger.info(
            f"Successfully ingested {qdrant_count} products to Qdrant.")
    except Exception as e:
        logger.error(f"Failed to ingest to Qdrant: {e}")
        result["status"] = "partial_error"
        result["message"] += f"Qdrant Ingest Failed: {str(e)}. "

    if result["status"] == "success":
        result["message"] = f"Ingestion completed. Synced {qdrant_count} products in Qdrant."

    return result
