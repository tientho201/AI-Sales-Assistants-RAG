"""
Feedback Agent.
Processes and stores customer feedback regarding recommended commercial vehicles.
"""
from app.database import SessionLocal
from app.models import UserFeedback
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class FeedbackAgent:
    def run(self, session_id: str, product_id: str, feedback_type: str, comment: Optional[str] = None) -> Dict[str, Any]:
        """
        Stores user feedback in the database.
        Returns the saved feedback details.
        """
        db = SessionLocal()
        try:
            feedback = UserFeedback(
                session_id=session_id,
                product_id=product_id,
                feedback_type=feedback_type,  # 'like' or 'dislike'
                comment=comment
            )
            db.add(feedback)
            db.commit()
            db.refresh(feedback)
            
            logger.info(f"FeedbackAgent recorded feedback for session {session_id}, product {product_id}: {feedback_type}")
            return {
                "id": feedback.id,
                "session_id": feedback.session_id,
                "product_id": feedback.product_id,
                "feedback_type": feedback.feedback_type,
                "comment": feedback.comment,
                "created_at": feedback.created_at
            }
        except Exception as e:
            logger.error(f"Error storing feedback in FeedbackAgent: {e}")
            db.rollback()
            raise e
        finally:
            db.close()

feedback_agent = FeedbackAgent()
