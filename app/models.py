"""
SQLAlchemy database models for the Sales Copilot system.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    requirements = relationship("ExtractedRequirement", back_populates="session", uselist=False, cascade="all, delete-orphan")
    feedbacks = relationship("UserFeedback", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("chat_sessions.session_id", ondelete="CASCADE"), nullable=False)
    sender = Column(String(10), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationship
    session = relationship("ChatSession", back_populates="messages")


class ExtractedRequirement(Base):
    __tablename__ = "extracted_requirements"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("chat_sessions.session_id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Requirements fields
    budget = Column(Float, nullable=True)           # max price in millions VND (e.g. 500.0)
    payload = Column(Float, nullable=True)          # payload capacity in kg (e.g. 950.0)
    fuel_type = Column(String(50), nullable=True)     # Petrol, Diesel, Electric
    vehicle_type = Column(String(50), nullable=True)  # Van, Light Truck, Heavy Truck
    use_case = Column(String(100), nullable=True)     # Inner-city delivery, Long-distance transport, etc.
    location = Column(String(100), nullable=True)     # Area of operation
    cargo_type = Column(String(100), nullable=True)   # Type of goods (frozen, dry, heavy, etc.)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    session = relationship("ChatSession", back_populates="requirements")


class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), ForeignKey("chat_sessions.session_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(String(100), nullable=False)
    feedback_type = Column(String(20), nullable=False)  # 'like' or 'dislike'
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    session = relationship("ChatSession", back_populates="feedbacks")
