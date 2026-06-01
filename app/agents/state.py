"""
LangGraph state definitions.
Stores state variables passed between agents.
"""
from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    # User input and metadata
    session_id: str
    user_message: str
    
    # Database structures retrieved in the workflow
    chat_history: List[Dict[str, Any]]
    
    # State tracking requirement values
    current_requirements: Dict[str, Any]
    newly_extracted: Dict[str, Any]
    
    # Decision flags
    clarification_needed: bool
    clarification_message: Optional[str]
    
    # Retrieval and recommendations
    retrieved_products: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    
    # Final outputs
    assistant_response: str
