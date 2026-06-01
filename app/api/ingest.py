"""
FastAPI router for product ingestion.
"""
from fastapi import APIRouter, HTTPException, Query
from app.services.product_service import ingest_products_from_csv
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

@router.post("/products")
def ingest_products_endpoint(csv_path: Optional[str] = Query(None, description="Absolute or relative path to CSV file")):
    """
    Ingests products from a CSV file into both Qdrant Vector DB and Neo4j Graph DB.
    Defaults to 'data/products.csv' if no path is provided.
    """
    # Resolve default CSV path relative to project root instead of CWD
    if not csv_path:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        csv_path = os.path.join(project_root, "data", "products.csv")
        
    if not os.path.exists(csv_path):
        logger.error(f"CSV file not found at path: {csv_path}")
        raise HTTPException(
            status_code=404,
            detail=f"CSV file not found at: {csv_path}. Please make sure you have created the CSV file."
        )
        
    try:
        logger.info(f"Triggering ingestion pipeline from: {csv_path}")
        result = ingest_products_from_csv(csv_path)
        
        if result["status"] == "partial_error":
            raise HTTPException(status_code=207, detail=result)  # Multi-status partial content error
            
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Ingestion API failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
