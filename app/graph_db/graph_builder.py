"""
Ingestion services for Neo4j Graph Database.
Generates nodes and relationships for commercial vehicles.
"""
from app.graph_db.neo4j_client import execute_cypher, get_neo4j_driver
import pandas as pd
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_price_range_label(price: float) -> str:
    """
    Categorizes numeric price into a standard PriceRange label.
    """
    if price < 300:
        return "Dưới 300 triệu"
    elif price <= 500:
        return "Từ 300 đến 500 triệu"
    elif price <= 800:
        return "Từ 500 đến 800 triệu"
    else:
        return "Trên 800 triệu"

def get_payload_range_label(payload: float) -> str:
    """
    Categorizes numeric payload capacity (in kg) into a standard PayloadRange label.
    """
    if payload < 1000:
        return "Dưới 1 tấn"
    elif payload <= 2500:
        return "Từ 1 đến 2.5 tấn"
    else:
        return "Trên 2.5 tấn"

def ingest_product_to_neo4j(product: Dict[str, Any]) -> None:
    """
    Creates/updates a Product node and its relationships to metadata entities in Neo4j.
    """
    driver = get_neo4j_driver()
    if driver is None:
        logger.warning("Neo4j driver not available. Skipping graph ingestion.")
        return

    price = float(product.get("price", 0))
    payload = float(product.get("payload", 0))
    
    price_range = get_price_range_label(price)
    payload_range = get_payload_range_label(payload)
    
    # Define parameterized Cypher query to insert nodes & relationships
    query = """
    // 1. Create or update Product Node
    MERGE (p:Product {product_id: $product_id})
    SET p.model = $model,
        p.brand = $brand,
        p.price = $price,
        p.payload = $payload,
        p.fuel_type = $fuel_type,
        p.vehicle_type = $vehicle_type,
        p.use_case = $use_case,
        p.description = $description

    // 2. Create and connect Brand
    MERGE (b:Brand {name: $brand})
    MERGE (p)-[:BELONGS_TO]->(b)

    // 3. Create and connect VehicleType
    MERGE (vt:VehicleType {name: $vehicle_type})
    MERGE (p)-[:HAS_TYPE]->(vt)

    // 4. Create and connect FuelType
    MERGE (ft:FuelType {name: $fuel_type})
    MERGE (p)-[:USES_FUEL]->(ft)

    // 5. Create and connect UseCase
    MERGE (uc:UseCase {name: $use_case})
    MERGE (p)-[:SUITABLE_FOR]->(uc)

    // 6. Create and connect PriceRange
    MERGE (pr:PriceRange {name: $price_range})
    MERGE (p)-[:IN_PRICE_RANGE]->(pr)

    // 7. Create and connect PayloadRange
    MERGE (plr:PayloadRange {name: $payload_range})
    MERGE (p)-[:HAS_PAYLOAD_RANGE]->(plr)
    """
    
    params = {
        "product_id": str(product.get("product_id")),
        "model": str(product.get("model")),
        "brand": str(product.get("brand")),
        "price": price,
        "payload": payload,
        "fuel_type": str(product.get("fuel_type")),
        "vehicle_type": str(product.get("vehicle_type")),
        "use_case": str(product.get("use_case")),
        "description": str(product.get("description", "")),
        "price_range": price_range,
        "payload_range": payload_range
    }
    
    try:
        execute_cypher(query, params)
        logger.info(f"Ingested product '{product.get('model')}' into Neo4j successfully.")
    except Exception as e:
        logger.error(f"Failed to ingest product '{product.get('model')}' into Neo4j: {e}")
        raise e

def ingest_csv_to_neo4j(csv_path: str) -> int:
    """
    Ingests all products from a CSV into Neo4j database.
    """
    try:
        df = pd.read_csv(csv_path)
        count = 0
        for _, row in df.iterrows():
            product_dict = row.to_dict()
            ingest_product_to_neo4j(product_dict)
            count += 1
        return count
    except Exception as e:
        logger.error(f"Error reading CSV for Neo4j ingestion: {e}")
        raise e

def clear_neo4j_database() -> None:
    """
    Deletes all nodes and relationships in Neo4j database. Use with caution.
    """
    query = "MATCH (n) DETACH DELETE n"
    try:
        execute_cypher(query)
        logger.info("Cleared all data from Neo4j database successfully.")
    except Exception as e:
        logger.error(f"Failed to clear Neo4j database: {e}")
