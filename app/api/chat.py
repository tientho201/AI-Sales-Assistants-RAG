"""
FastAPI router for conversational sales copilot endpoint.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ChatRequest, ChatResponse, RequirementBase
from app.services.chat_history_service import add_chat_message
from app.agents.graph import sales_copilot_graph
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/", response_model=ChatResponse)
def post_chat_endpoint(payload: ChatRequest, db: Session = Depends(get_db)):
    """
    Handles user chat messages.
    Logs user message, runs LangGraph agent pipeline, logs assistant response, and returns response payload.
    """
    try:
        session_id = payload.session_id
        user_message = payload.message
        
        logger.info(f"Received message from session {session_id}: '{user_message}'")
        
        # 1. Log the user message to SQLite/PostgreSQL
        add_chat_message(db, session_id, sender="user", content=user_message)
        
        # 2. Prepare initial state for LangGraph execution
        initial_state = {
            "session_id": session_id,
            "user_message": user_message,
            "chat_history": [],  # Synced dynamically inside graph nodes
            "current_requirements": {},
            "newly_extracted": {},
            "clarification_needed": False,
            "clarification_message": None,
            "retrieved_products": [],
            "recommendations": [],
            "assistant_response": ""
        }
        
        # 3. Invoke LangGraph Orchestrator
        logger.info("Invoking Multi-Agent LangGraph workflow...")
        final_state = sales_copilot_graph.invoke(initial_state)
        
        # 4. Extract final state values
        response_text = final_state.get("assistant_response", "Dạ, em chưa thể xử lý yêu cầu lúc này. Anh/chị vui lòng thử lại sau.")
        clarification_needed = final_state.get("clarification_needed", False)
        current_reqs = final_state.get("current_requirements", {})
        recommendations = final_state.get("recommendations", [])
        
        # 5. Log the assistant response to database
        add_chat_message(db, session_id, sender="assistant", content=response_text)
        
        # Format requirements schema
        req_schema = RequirementBase(**current_reqs) if current_reqs else None
        
        return ChatResponse(
            session_id=session_id,
            response=response_text,
            clarification_needed=clarification_needed,
            requirements=req_schema,
            recommendations=recommendations
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat execution failed: {str(e)}")
