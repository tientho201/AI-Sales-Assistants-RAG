"""
Product service managing CSV ingestion into both Qdrant and Neo4j.
"""
from app.vector.vector_builder import ingest_csv_to_qdrant
from app.graph_db.graph_builder import ingest_csv_to_neo4j, clear_neo4j_database
from app.graph_db.neo4j_client import get_neo4j_driver
from app.vector.qdrant_client import get_qdrant_client
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def ingest_products_from_csv(csv_path: str) -> Dict[str, Any]:
    """
    Ingests product data from CSV file into both Qdrant and Neo4j databases.
    Enforces parallel consistency.
    """
    result = {
        "status": "success",
        "qdrant_count": 0,
        "neo4j_count": 0,
        "message": ""
    }
    
    # 1. Ingest to Qdrant Vector DB
    try:
        qdrant_count = ingest_csv_to_qdrant(csv_path)
        result["qdrant_count"] = qdrant_count
        logger.info(f"Successfully ingested {qdrant_count} products to Qdrant.")
    except Exception as e:
        logger.error(f"Failed to ingest to Qdrant: {e}")
        result["status"] = "partial_error"
        result["message"] += f"Qdrant Ingest Failed: {str(e)}. "

    # 2. Ingest to Neo4j Graph DB
    try:
        # Clear Neo4j first to avoid duplicates
        clear_neo4j_database()
        
        neo4j_count = ingest_csv_to_neo4j(csv_path)
        result["neo4j_count"] = neo4j_count
        logger.info(f"Successfully ingested {neo4j_count} products to Neo4j.")
    except Exception as e:
        logger.error(f"Failed to ingest to Neo4j: {e}")
        result["status"] = "partial_error"
        result["message"] += f"Neo4j Ingest Failed: {str(e)}. "

    if result["status"] == "success":
        result["message"] = f"Ingestion completed. Synced {qdrant_count} products in Qdrant and Neo4j."
        
    return result
