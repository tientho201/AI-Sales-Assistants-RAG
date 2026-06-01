"""
Service to manage and sync extracted customer requirements in the database.
"""
from sqlalchemy.orm import Session
from app.models import ExtractedRequirement, ChatSession
from app.services.chat_history_service import get_or_create_session
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

def get_requirements(db: Session, session_id: str) -> Dict[str, Any]:
    """
    Retrieves aggregated customer requirements for a given session.
    Returns empty dict if no requirements are saved.
    """
    req = db.query(ExtractedRequirement).filter(ExtractedRequirement.session_id == session_id).first()
    if not req:
        return {}
        
    return {
        "budget": req.budget,
        "payload": req.payload,
        "fuel_type": req.fuel_type,
        "vehicle_type": req.vehicle_type,
        "use_case": req.use_case,
        "location": req.location,
        "cargo_type": req.cargo_type
    }

def save_requirements(db: Session, session_id: str, data: Dict[str, Any]) -> ExtractedRequirement:
    """
    Saves or updates aggregated customer requirements in the database.
    """
    # Ensure session exists
    get_or_create_session(db, session_id)
    
    req = db.query(ExtractedRequirement).filter(ExtractedRequirement.session_id == session_id).first()
    
    if not req:
        logger.info(f"Creating new extracted requirements row for session: {session_id}")
        req = ExtractedRequirement(
            session_id=session_id,
            budget=data.get("budget"),
            payload=data.get("payload"),
            fuel_type=data.get("fuel_type"),
            vehicle_type=data.get("vehicle_type"),
            use_case=data.get("use_case"),
            location=data.get("location"),
            cargo_type=data.get("cargo_type")
        )
        db.add(req)
    else:
        logger.info(f"Updating existing requirements row for session: {session_id}")
        req.budget = data.get("budget")
        req.payload = data.get("payload")
        req.fuel_type = data.get("fuel_type")
        req.vehicle_type = data.get("vehicle_type")
        req.use_case = data.get("use_case")
        req.location = data.get("location")
        req.cargo_type = data.get("cargo_type")
        
    db.commit()
    db.refresh(req)
    return req
