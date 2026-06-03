"""
Pydantic schemas for data validation.
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# Extracted requirements schema


class CustomerProfile(BaseModel):
    customer_id: Optional[str] = Field(
        None, description="Unique customer identifier")
    budget_min: Optional[float] = Field(
        None, description="Min budget in millions VND")
    budget_max: Optional[float] = Field(
        None, description="Max budget in millions VND")
    payload_min: Optional[float] = Field(
        None, description="Min payload capacity in kg")
    payload_max: Optional[float] = Field(
        None, description="Max payload capacity in kg")
    fuel_type: Optional[str] = Field(
        None, description="Petrol, Diesel, or Electric")
    vehicle_type: Optional[str] = Field(
        None, description="Van, Light Truck, Heavy Truck")
    use_case: Optional[str] = Field(
        None, description="Inner-city, Long-distance, cargo etc.")
    location: Optional[str] = Field(None, description="Operational location")
    cargo_type: Optional[str] = Field(None, description="Type of cargo loaded")
    preferred_brand: Optional[str] = Field(
        None, description="Preferred vehicle brand")
    financing_required: Optional[bool] = Field(
        None, description="Whether financing is required")
    urgency: Optional[str] = Field(
        None, description="Urgency level (low, medium, high, urgent)")
    contact_name: Optional[str] = Field(
        None, description="Contact person name")
    contact_phone: Optional[str] = Field(
        None, description="Contact phone number")
    contact_email: Optional[str] = Field(
        None, description="Contact email address")
    profile_confidence: Optional[float] = Field(
        None, description="Confidence score of the profile (0-1)")
    extra_requirements: Optional[Dict[str, Any]] = Field(
        None, description="Additional extracted requirements")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CustomerProfileCreate(CustomerProfile):
    session_id: str
    customer_id: str


class CustomerProfileResponse(CustomerProfile):
    id: int
    session_id: str
    updated_at: datetime

    class Config:
        from_attributes = True


class RequirementBase(CustomerProfile):
    pass


# Memory Event schemas
class MemoryEventBase(BaseModel):
    field_name: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    confidence: float = 0.0
    event_type: str = "update"
    status: str = "applied"
    reason: Optional[str] = None
    extracted_by: Optional[str] = None


class MemoryEventCreate(MemoryEventBase):
    session_id: str
    message_id: Optional[int] = None


class MemoryEventResponse(MemoryEventBase):
    id: int
    session_id: str
    message_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Message schemas


class MessageBase(BaseModel):
    sender: str = Field(..., description="'user' or 'assistant'")
    content: str
    message_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Metadata associated with the message")


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
    customer_profile: Optional[CustomerProfile] = None
    requirements: Optional[CustomerProfile] = None
    memory_events: List[MemoryEventResponse] = []

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
    customer_profile: Optional[CustomerProfile] = None
    requirements: Optional[CustomerProfile] = None
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
    message_id: Optional[int] = None
    product_id: str
    feedback_type: str = Field(..., description="'like' or 'dislike'")
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    session_id: str
    message_id: Optional[int] = None
    product_id: str
    feedback_type: str
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
