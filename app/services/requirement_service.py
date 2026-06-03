"""
Service to manage and sync extracted customer requirements in the database.
"""
from sqlalchemy.orm import Session
from app.models import CustomerProfile, ChatSession
from app.services.chat_history_service import get_or_create_session
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def get_requirements(db: Session, session_id: str) -> Dict[str, Any]:
    """
    Retrieves aggregated customer requirements for a given session.
    Returns empty dict if no requirements are saved.
    """
    req = db.query(CustomerProfile).filter(
        CustomerProfile.session_id == session_id).first()
    if not req:
        return {}

    return {
        "customer_id": req.customer_id,
        "budget_min": req.budget_min,
        "budget_max": req.budget_max,
        "payload_min": req.payload_min,
        "payload_max": req.payload_max,
        "fuel_type": req.fuel_type,
        "vehicle_type": req.vehicle_type,
        "use_case": req.use_case,
        "location": req.location,
        "cargo_type": req.cargo_type,
        "preferred_brand": req.preferred_brand,
        "financing_required": req.financing_required,
        "urgency": req.urgency,
        "contact_name": req.contact_name,
        "contact_phone": req.contact_phone,
        "contact_email": req.contact_email,
        "profile_confidence": req.profile_confidence,
        "extra_requirements": req.extra_requirements,
        "created_at": req.created_at,
        "updated_at": req.updated_at
    }


def save_requirements(db: Session, session_id: str, data: Dict[str, Any]) -> CustomerProfile:
    """
    Saves or updates aggregated customer requirements in the database.
    """
    # Ensure session exists
    get_or_create_session(db, session_id)

    req = db.query(CustomerProfile).filter(
        CustomerProfile.session_id == session_id).first()

    if not req:
        logger.info(
            f"Creating new extracted requirements row for session: {session_id}")
        req = CustomerProfile(
            session_id=session_id,
            customer_id=data.get("customer_id"),
            budget_min=data.get("budget_min"),
            budget_max=data.get("budget_max"),
            payload_min=data.get("payload_min"),
            payload_max=data.get("payload_max"),
            fuel_type=data.get("fuel_type"),
            vehicle_type=data.get("vehicle_type"),
            use_case=data.get("use_case"),
            location=data.get("location"),
            cargo_type=data.get("cargo_type"),
            preferred_brand=data.get("preferred_brand"),
            financing_required=data.get("financing_required"),
            urgency=data.get("urgency"),
            contact_name=data.get("contact_name"),
            contact_phone=data.get("contact_phone"),
            contact_email=data.get("contact_email"),
            profile_confidence=data.get("profile_confidence"),
            extra_requirements=data.get("extra_requirements"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
        db.add(req)
    else:
        logger.info(
            f"Updating existing requirements row for session: {session_id}")
        req.customer_id = data.get("customer_id")
        req.budget_min = data.get("budget_min")
        req.budget_max = data.get("budget_max")
        req.payload_min = data.get("payload_min")
        req.payload_max = data.get("payload_max")
        req.fuel_type = data.get("fuel_type")
        req.vehicle_type = data.get("vehicle_type")
        req.use_case = data.get("use_case")
        req.location = data.get("location")
        req.cargo_type = data.get("cargo_type")
        req.preferred_brand = data.get("preferred_brand")
        req.financing_required = data.get("financing_required")
        req.urgency = data.get("urgency")
        req.contact_name = data.get("contact_name")
        req.contact_phone = data.get("contact_phone")
        req.contact_email = data.get("contact_email")
        req.profile_confidence = data.get("profile_confidence")
        req.extra_requirements = data.get("extra_requirements")
        req.created_at = data.get("created_at")
        req.updated_at = data.get("updated_at")

    db.commit()
    db.refresh(req)
    return req
