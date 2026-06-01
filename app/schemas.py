"""
Pydantic schemas for data validation.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# Extracted requirements schema
class RequirementBase(BaseModel):
    budget: Optional[float] = Field(None, description="Max budget in millions VND")
    payload: Optional[float] = Field(None, description="Payload capacity in kg")
    fuel_type: Optional[str] = Field(None, description="Petrol, Diesel, or Electric")
    vehicle_type: Optional[str] = Field(None, description="Van, Light Truck, Heavy Truck")
    use_case: Optional[str] = Field(None, description="Inner-city, Long-distance, cargo etc.")
    location: Optional[str] = Field(None, description="Operational location")
    cargo_type: Optional[str] = Field(None, description="Type of cargo loaded")

class RequirementCreate(RequirementBase):
    session_id: str

class RequirementResponse(RequirementBase):
    id: int
    session_id: str
    updated_at: datetime

    class Config:
        from_attributes = True

# Message schemas
class MessageBase(BaseModel):
    sender: str = Field(..., description="'user' or 'assistant'")
    content: str

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# Session schemas
class SessionCreate(BaseModel):
    session_id: str

class SessionResponse(BaseModel):
    id: int
    session_id: str
    created_at: datetime
    messages: List[MessageResponse] = []
    requirements: Optional[RequirementBase] = None

    class Config:
        from_attributes = True

# Chat schemas
class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    response: str
    clarification_needed: bool
    requirements: Optional[RequirementBase] = None
    recommendations: List[Dict[str, Any]] = []

# Product schemas
class ProductBase(BaseModel):
    product_id: str
    brand: str
    model: str
    price: float
    payload: float
    fuel_type: str
    vehicle_type: str
    use_case: str
    description: str

class ProductSearchRequest(BaseModel):
    query: str
    top_k: int = 3

# Feedback schemas
class FeedbackRequest(BaseModel):
    session_id: str
    product_id: str
    feedback_type: str = Field(..., description="'like' or 'dislike'")
    comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: int
    session_id: str
    product_id: str
    feedback_type: str
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
