"""
SQLAlchemy database models for the Sales Copilot system.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, JSON, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer_id = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)
    # Relationships
    messages = relationship(
        "ChatMessage", back_populates="session", cascade="all, delete-orphan")
    requirements = relationship(
        "ExtractedRequirement", back_populates="session", uselist=False, cascade="all, delete-orphan")
    feedbacks = relationship(
        "UserFeedback", back_populates="session", cascade="all, delete-orphan")
    customer_profile = relationship(
        "CustomerProfile",
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
    )
    memory_events = relationship(
        "MemoryEvent",
        back_populates="session",
        cascade="all, delete-orphan",
    )


class CustomerProfile(Base):
    """
    Current structured memory of a customer/session.

    This table stores the latest known state.
    It should not be treated as historical truth.
    Historical changes are stored in MemoryEvent.
    """
    __tablename__ = "customer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey(
        "chat_sessions.session_id", ondelete="CASCADE"), unique=True, nullable=False)

    customer_id = Column(String(100), index=True, nullable=False)

    budget_min = Column(Float, nullable=True)
    budget_max = Column(Float, nullable=True)

    payload_min = Column(Float, nullable=True)
    payload_max = Column(Float, nullable=True)

    fuel_type = Column(String(50), nullable=True)
    vehicle_type = Column(String(50), nullable=True)
    use_case = Column(String(150), nullable=True)
    location = Column(String(150), nullable=True)
    cargo_type = Column(String(150), nullable=True)

    preferred_brand = Column(String(100), nullable=True)
    financing_required = Column(Boolean, nullable=True)

    urgency = Column(String(50), nullable=True)
    # low, medium, high, urgent

    contact_name = Column(String(100), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    contact_email = Column(String(150), nullable=True)

    # Confidence for the whole profile
    profile_confidence = Column(Float, default=0.0)

    # Store uncertain / extra extracted data
    extra_requirements = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    session = relationship("ChatSession", back_populates="customer_profile")

# Customer changing their minds


class MemoryEvent(Base):
    """Important events or details from the conversation (e.g., last purchase, preferences)."""
    __tablename__ = "memory_events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey(
        "chat_sessions.session_id", ondelete="CASCADE"), nullable=False)
    message_id = Column(Integer, ForeignKey(
        "chat_messages.id", ondelete="CASCADE"), nullable=True)

    field_name = Column(String(100), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)

    confidence = Column(Float, default=0.0)

    event_type = Column(String(50), nullable=False, default="update")
    # create, update, delete, confirm, conflict, reject

    status = Column(String(50), nullable=False, default="applied")
    # pending, applied, rejected, needs_confirmation

    reason = Column(Text, nullable=True)

    extracted_by = Column(String(100), nullable=True)
    # requirement_agent, memory_agent, human_agent

    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="memory_events")

    source_message = relationship(
        "ChatMessage",
        back_populates="memory_events",
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey(
        "chat_sessions.session_id", ondelete="CASCADE"), nullable=False)
    sender = Column(String(10), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    message_metadata = Column(JSON, nullable=True)
    # Relationship
    session = relationship("ChatSession", back_populates="messages")
    memory_events = relationship(
        "MemoryEvent",
        back_populates="source_message",
    )


class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey(
        "chat_sessions.session_id", ondelete="CASCADE"), nullable=False)
    message_id = Column(Integer, ForeignKey(
        "chat_messages.id", ondelete="CASCADE"), nullable=True)

    product_id = Column(String(100), nullable=False)
    feedback_type = Column(String(20), nullable=False)  # 'like' or 'dislike'
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    session = relationship("ChatSession", back_populates="feedbacks")
