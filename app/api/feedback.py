"""
FastAPI router for user feedback capturing.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import FeedbackRequest, FeedbackResponse
from app.agents.feedback_agent import feedback_agent
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedback", tags=["Feedback"])

@router.post("/", response_model=FeedbackResponse)
def post_feedback_endpoint(payload: FeedbackRequest, db: Session = Depends(get_db)):
    """
    Submits and stores user feedback (like/dislike) for a specific product recommendations.
    """
    try:
        logger.info(f"Submitting feedback for session {payload.session_id}, product {payload.product_id}")
        
        # Invoke FeedbackAgent to record in DB
        result = feedback_agent.run(
            session_id=payload.session_id,
            product_id=payload.product_id,
            feedback_type=payload.feedback_type,
            comment=payload.comment
        )
        return result
    except Exception as e:
        logger.error(f"Failed to post feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Feedback log failed: {str(e)}")
