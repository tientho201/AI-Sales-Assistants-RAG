"""
Hybrid search utilities combining Qdrant Vector Search and BM25 Lexical Search.
"""
import os
import pandas as pd
from typing import List, Dict, Any
import bm25s
import logging

logger = logging.getLogger(__name__)

def load_products_from_csv() -> List[Dict[str, Any]]:
    """
    Loads product data from the CSV file.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    csv_path = os.path.join(project_root, "data", "products.csv")
    
    if not os.path.exists(csv_path):
        logger.error(f"Products CSV file not found at: {csv_path}")
        return []
        
    try:
        df = pd.read_csv(csv_path)
        # Fill NaN values with empty string or sensible default
        df = df.fillna("")
        return df.to_dict(orient="records")
    except Exception as e:
        logger.error(f"Error reading products CSV: {e}")
        return []

def make_product_text(product: Dict[str, Any]) -> str:
    """
    Creates a comprehensive description string for BM25 indexing.
    """
    return (
        f"Xe tải/xe van hãng {product.get('brand', '')} model {product.get('model', '')}. "
        f"Loại xe: {product.get('vehicle_type', '')}. Nhiên liệu: {product.get('fuel_type', '')}. "
        f"Tải trọng: {product.get('payload', 0)} kg. Giá: {product.get('price', 0)} triệu VND. "
        f"Ứng dụng phù hợp: {product.get('use_case', '')}. "
        f"Mô tả sản phẩm: {product.get('description', '')}"
    )

def search_bm25_products(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Performs lexical search on the product catalog using BM25.
    Returns a list of matching product dictionaries with 'score' key.
    """
    products = load_products_from_csv()
    if not products:
        return []
        
    # Generate index texts
    texts = [make_product_text(p) for p in products]
    
    # Initialize BM25 and fit index
    bm25 = bm25s.BM25()
    tokenized_texts = bm25s.tokenize(texts)
    bm25.index(tokenized_texts)
    
    # Tokenize query and search
    tokenized_query = bm25s.tokenize(query)
    indices, scores = bm25.retrieve(tokenized_query, k=min(top_k, len(products)))
    
    matched_products = []
    if indices.ndim > 1:
        query_indices = indices[0]
        query_scores = scores[0]
    else:
        query_indices = indices
        query_scores = scores
        
    for idx, score in zip(query_indices, query_scores):
        product = dict(products[idx])
        product["score"] = float(score)
        matched_products.append(product)
        
    logger.info(f"BM25 search found {len(matched_products)} products for query: '{query}'")
    return matched_products
