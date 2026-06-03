"""
Service to manage chat session histories and message logging in PostgreSQL/SQLite.
"""
from sqlalchemy.orm import Session
from app.models import ChatSession, ChatMessage
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def get_or_create_session(db: Session, session_id: str) -> ChatSession:
    """
    Retrieves an existing chat session or creates a new one if it doesn't exist.
    """
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id).first()
    if not session:
        logger.info(f"Creating new chat session: {session_id}")
        session = ChatSession(session_id=session_id)
        db.add(session)
        db.commit()
        db.refresh(session)
    return session


def get_session_history(db: Session, session_id: str) -> List[ChatMessage]:
    """
    Returns all logged messages for a session ordered chronologically.
    """
    get_or_create_session(db, session_id)
    return db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.timestamp.asc()).all()


def add_chat_message(db: Session, session_id: str, sender: str, content: str) -> ChatMessage:
    """
    Logs a new chat message (from user or assistant) in the database.
    """
    # Ensure session exists first
    get_or_create_session(db, session_id)

    message = ChatMessage(
        session_id=session_id,
        sender=sender,  # 'user' or 'assistant'
        content=content
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    logger.info(
        f"Log message saved in DB for session {session_id} by {sender}")
    return message


def list_all_sessions(db: Session) -> List[ChatSession]:
    """
    Lists all chat sessions stored in the database.
    """
    return db.query(ChatSession).order_by(ChatSession.created_at.desc()).all()
