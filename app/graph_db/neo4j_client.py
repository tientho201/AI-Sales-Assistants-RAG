"""
Neo4j Graph Database Client.
Supports both Local and Cloud (Aura) instances.
"""
from neo4j import GraphDatabase, Driver
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Global driver variable for reuse
_driver: Driver = None

def get_neo4j_driver() -> Driver:
    """
    Initializes and returns the Neo4j Driver instance.
    Uses cached global driver if available.
    """
    global _driver
    if _driver is not None:
        return _driver
        
    uri = settings.NEO4J_URI or "bolt://localhost:7687"
    username = settings.NEO4J_USERNAME or "neo4j"
    password = settings.NEO4J_PASSWORD or "password"
    
    try:
        logger.info(f"Connecting to Neo4j database at: {uri} (Username: {username})")
        # Initialize driver
        _driver = GraphDatabase.driver(uri, auth=(username, password))
        # Verify connectivity
        _driver.verify_connectivity()
        logger.info("Successfully connected to Neo4j database.")
        return _driver
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j: {e}")
        # Return none or mock if connection fails, so application doesn't crash on boot
        return None

def close_neo4j_driver() -> None:
    """
    Closes the global Neo4j driver.
    """
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None
        logger.info("Closed Neo4j driver connection.")

def execute_cypher(query: str, parameters: dict = None) -> list:
    """
    Utility function to execute a Cypher query on Neo4j database.
    Returns a list of dicts corresponding to query results.
    """
    driver = get_neo4j_driver()
    if driver is None:
        logger.warning("Neo4j Driver is not initialized. Cypher query ignored.")
        return []
        
    parameters = parameters or {}
    try:
        with driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]
    except Exception as e:
        logger.error(f"Error executing Cypher query: {e}\nQuery: {query}")
        return []
