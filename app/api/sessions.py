"""
FastAPI router for conversation session management.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import SessionResponse, MessageResponse, RequirementBase
from app.services.chat_history_service import list_all_sessions, get_session_history
from app.services.requirement_service import get_requirements
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.get("/", response_model=List[SessionResponse])
def get_all_sessions_endpoint(db: Session = Depends(get_db)):
    """
    Retrieves all stored conversation sessions.
    """
    try:
        sessions = list_all_sessions(db)
        response = []
        for s in sessions:
            response.append(SessionResponse(
                id=s.id,
                session_id=s.session_id,
                created_at=s.created_at,
                messages=[]  # Don't return all messages in list view for optimization
            ))
        return response
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}", response_model=SessionResponse)
def get_session_detail_endpoint(session_id: str, db: Session = Depends(get_db)):
    """
    Retrieves full details of a specific session, including message logs and current requirements state.
    """
    try:
        history = get_session_history(db, session_id)
        if not history:
            # Session is empty or just initialized
            from app.services.chat_history_service import get_or_create_session
            s = get_or_create_session(db, session_id)
            return SessionResponse(
                id=s.id,
                session_id=s.session_id,
                created_at=s.created_at,
                messages=[],
                requirements=None
            )
            
        # Get active session record
        session_record = history[0].session
        
        # Format messages list
        messages_response = [
            MessageResponse(
                id=m.id,
                sender=m.sender,
                content=m.content,
                timestamp=m.timestamp
            ) for m in history
        ]
        
        # Load accumulated requirements
        req_dict = get_requirements(db, session_id)
        req_schema = RequirementBase(**req_dict) if req_dict else None
        
        return SessionResponse(
            id=session_record.id,
            session_id=session_record.session_id,
            created_at=session_record.created_at,
            messages=messages_response,
            requirements=req_schema
        )
    except Exception as e:
        logger.error(f"Error fetching session details for {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
