"""
Services to ingest products into Qdrant Vector Database.
"""
from qdrant_client.http import models as rest_models
from app.config import settings
from app.vector.qdrant_client import get_qdrant_client, init_qdrant_collection
from app.vector.embeddings import embedding_service
import pandas as pd
import logging
import uuid
from typing import Dict, Any

logger = logging.getLogger(__name__)

def make_product_text(product: Dict[str, Any]) -> str:
    """
    Creates a comprehensive description string for vector indexing based on product attributes.
    """
    return (
        f"Xe tải/xe van hãng {product.get('brand', '')} model {product.get('model', '')}. "
        f"Loại xe: {product.get('vehicle_type', '')}. Nhiên liệu: {product.get('fuel_type', '')}. "
        f"Tải trọng: {product.get('payload', 0)} kg. Giá: {product.get('price', 0)} triệu VND. "
        f"Ứng dụng phù hợp: {product.get('use_case', '')}. "
        f"Mô tả sản phẩm: {product.get('description', '')}"
    )

def upsert_product_to_qdrant(product: Dict[str, Any]) -> None:
    """
    Ingests a single product into Qdrant collection.
    Generates embedding for product_text and stores metadata.
    """
    client = get_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION_NAME or "truck_products"
    
    product_id = str(product.get('product_id', uuid.uuid4()))
    product_text = make_product_text(product)
    
    # Generate embedding vector
    vector = embedding_service.get_embedding(product_text)
    
    # Store metadata exactly as specified in requirements
    payload = {
        "product_id": product_id,
        "product_text": product_text,
        "brand": product.get("brand"),
        "model": product.get("model"),
        "price": float(product.get("price", 0)),
        "payload": float(product.get("payload", 0)),
        "fuel_type": product.get("fuel_type"),
        "vehicle_type": product.get("vehicle_type"),
        "use_case": product.get("use_case"),
        "description": product.get("description", "")
    }
    
    try:
        client.upsert(
            collection_name=collection_name,
            points=[
                rest_models.PointStruct(
                    id=hash(product_id) % (10**9),  # Numerical Qdrant ID from string UUID
                    vector=vector,
                    payload=payload
                )
            ]
        )
        logger.info(f"Upserted product {product_id} to Qdrant successfully.")
    except Exception as e:
        logger.error(f"Error upserting product {product_id} to Qdrant: {e}")
        raise e

def ingest_csv_to_qdrant(csv_path: str) -> int:
    """
    Reads products from a CSV file and batch upserts them to Qdrant.
    """
    # Ensure collection is created
    init_qdrant_collection()
    
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"Read {len(df)} products from CSV: {csv_path}")
        
        count = 0
        for _, row in df.iterrows():
            product_dict = row.to_dict()
            # Ensure price and payload are numeric
            product_dict['price'] = float(product_dict.get('price', 0))
            product_dict['payload'] = float(product_dict.get('payload', 0))
            
            upsert_product_to_qdrant(product_dict)
            count += 1
            
        return count
    except Exception as e:
        logger.error(f"Error during CSV ingestion to Qdrant: {e}")
        raise e
