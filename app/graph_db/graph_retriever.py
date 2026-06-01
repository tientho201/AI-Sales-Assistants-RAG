"""
Retrieval services for Neo4j Graph Database.
Translates search requirements into high-performance Cypher Queries.
"""
from app.config import settings
from app.graph_db.neo4j_client import execute_cypher, get_neo4j_driver
from app.graph_db.graph_builder import get_price_range_label, get_payload_range_label
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

def map_vietnamese_attributes(reqs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Helper to normalize fuel types or vehicle types into standardized database names if needed.
    """
    mapped = reqs.copy()
    
    # Map common fuel types in Vietnamese
    fuel = mapped.get("fuel_type")
    if fuel:
        fuel_lower = fuel.lower()
        if " xăng" in fuel_lower or fuel_lower == "xăng" or fuel_lower == "petrol":
            mapped["fuel_type"] = "Xăng"
        elif "dầu" in fuel_lower or "diesel" in fuel_lower:
            mapped["fuel_type"] = "Dầu"
        elif "điện" in fuel_lower or "electric" in fuel_lower:
            mapped["fuel_type"] = "Điện"
            
    # Map common vehicle types in Vietnamese
    vtype = mapped.get("vehicle_type")
    if vtype:
        vtype_lower = vtype.lower()
        if "van" in vtype_lower or "xe van" in vtype_lower:
            mapped["vehicle_type"] = "Van"
        elif "tải nhẹ" in vtype_lower or "light truck" in vtype_lower:
            mapped["vehicle_type"] = "Xe tải nhẹ"
        elif "tải nặng" in vtype_lower or "heavy truck" in vtype_lower:
            mapped["vehicle_type"] = "Xe tải nặng"
            
    return mapped

def search_graph_products(requirements: Dict[str, Any], top_k: int = None) -> List[Dict[str, Any]]:
    """
    Searches Neo4j for products matching requirements.
    Uses relational matching and ranks products by match_score (number of matched conditions).
    """
    driver = get_neo4j_driver()
    if driver is None:
        logger.warning("Neo4j driver is not active. Returning empty list.")
        return []
        
    limit = top_k or settings.GRAPH_TOP_K or 5
    
    # Normalize requirements for DB compatibility
    norm_reqs = map_vietnamese_attributes(requirements)
    
    brand = norm_reqs.get("brand")
    fuel_type = norm_reqs.get("fuel_type")
    vehicle_type = norm_reqs.get("vehicle_type")
    use_case = norm_reqs.get("use_case")
    
    # Map raw numeric requirements to range labels
    price_range = None
    if norm_reqs.get("budget") is not None:
        price_range = get_price_range_label(float(norm_reqs["budget"]))
        
    payload_range = None
    if norm_reqs.get("payload") is not None:
        payload_range = get_payload_range_label(float(norm_reqs["payload"]))

    # Intelligent ranking Cypher query based on how many constraints a product satisfies
    cypher_query = """
    MATCH (p:Product)
    
    // Optional matches to compute scoring
    OPTIONAL MATCH (p)-[:BELONGS_TO]->(b:Brand) 
    WHERE $brand IS NOT NULL AND b.name = $brand
    
    OPTIONAL MATCH (p)-[:USES_FUEL]->(ft:FuelType) 
    WHERE $fuel_type IS NOT NULL AND ft.name = $fuel_type
    
    OPTIONAL MATCH (p)-[:HAS_TYPE]->(vt:VehicleType) 
    WHERE $vehicle_type IS NOT NULL AND vt.name = $vehicle_type
    
    OPTIONAL MATCH (p)-[:SUITABLE_FOR]->(uc:UseCase) 
    WHERE $use_case IS NOT NULL AND uc.name CONTAINS $use_case
    
    OPTIONAL MATCH (p)-[:IN_PRICE_RANGE]->(pr:PriceRange) 
    WHERE $price_range IS NOT NULL AND pr.name = $price_range
    
    OPTIONAL MATCH (p)-[:HAS_PAYLOAD_RANGE]->(plr:PayloadRange) 
    WHERE $payload_range IS NOT NULL AND plr.name = $payload_range
    
    WITH p,
         ((CASE WHEN b IS NOT NULL THEN 1.5 ELSE 0.0 END) + // Higher weight for matching brand/fuel/type
          (CASE WHEN ft IS NOT NULL THEN 1.2 ELSE 0.0 END) +
          (CASE WHEN vt IS NOT NULL THEN 1.2 ELSE 0.0 END) +
          (CASE WHEN uc IS NOT NULL THEN 1.0 ELSE 0.0 END) +
          (CASE WHEN pr IS NOT NULL THEN 1.0 ELSE 0.0 END) +
          (CASE WHEN plr IS NOT NULL THEN 1.0 ELSE 0.0 END)) AS match_score
          
    WHERE match_score > 0
    RETURN p.product_id AS product_id,
           p.brand AS brand,
           p.model AS model,
           p.price AS price,
           p.payload AS payload,
           p.fuel_type AS fuel_type,
           p.vehicle_type AS vehicle_type,
           p.use_case AS use_case,
           p.description AS description,
           match_score
    ORDER BY match_score DESC, price ASC
    LIMIT $limit
    """
    
    params = {
        "brand": brand,
        "fuel_type": fuel_type,
        "vehicle_type": vehicle_type,
        "use_case": use_case,
        "price_range": price_range,
        "payload_range": payload_range,
        "limit": limit
    }
    
    try:
        results = execute_cypher(cypher_query, params)
        logger.info(f"Neo4j graph query retrieved {len(results)} matches for criteria: {params}")
        return results
    except Exception as e:
        logger.error(f"Error during graph product search: {e}")
        return []
