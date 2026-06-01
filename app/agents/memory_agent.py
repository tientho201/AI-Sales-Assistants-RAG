"""
Memory Agent.
Loads previous requirements from database, merges them with newly extracted requirements,
and updates the current aggregated requirements state.
"""
from app.database import SessionLocal
from app.services.requirement_service import get_requirements, save_requirements
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class MemoryAgent:
    def run(self, session_id: str, newly_extracted: Dict[str, Any]) -> Dict[str, Any]:
        """
        Loads existing session requirements from DB, merges newly extracted attributes,
        saves the merged results, and returns the unified requirement state.
        """
        db = SessionLocal()
        try:
            # 1. Retrieve existing requirements from PostgreSQL
            existing = get_requirements(db, session_id)
            
            # 2. Merge logic: new values override old values, old values are preserved if new is None
            merged = {}
            keys = ["budget", "payload", "fuel_type", "vehicle_type", "use_case", "location", "cargo_type"]
            
            for key in keys:
                new_val = newly_extracted.get(key)
                old_val = existing.get(key) if existing else None
                
                if new_val is not None:
                    merged[key] = new_val
                else:
                    merged[key] = old_val
            
            # 3. Save the merged requirements back to database
            save_requirements(db, session_id, merged)
            
            logger.info(f"MemoryAgent merged requirements for session {session_id}: {merged}")
            return merged
        except Exception as e:
            logger.error(f"Error in MemoryAgent: {e}")
            # In case of DB failures, return merged in-memory as fallback
            return newly_extracted
        finally:
            db.close()

memory_agent = MemoryAgent()
