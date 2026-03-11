from fastapi import APIRouter, Depends, HTTPException
import traceback
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Lead
from inference import assign_priorities, score_lead_instance
from nlp.processor import analyze_conversation
from ml.conversation_features import update_conversation_features
from schemas import ConversationRequest

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/leads/{lead_id}/conversation")
def add_conversation(lead_id: int, request: ConversationRequest, db: Session = Depends(get_db)):
    try:
        lead = db.query(Lead).filter(Lead.lead_id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        # Step 1: NLP
        new_features = analyze_conversation(request.text)

        # Step 2: Update aggregated conversation features
        update_conversation_features(lead, new_features)

        # Step 3: Re-run ML inference (keeping existing scoring philosophy)
        new_score = score_lead_instance(lead)

        lead.score = new_score

        db.commit()
        db.refresh(lead)

        # Preserve percentile-based prioritization
        assign_priorities()

        return {
            "lead_id": lead.lead_id,
            "score": new_score,
            "priority": lead.priority,
            "avg_intent_score": lead.avg_intent_score,
            "avg_urgency_score": lead.avg_urgency_score,
            "avg_sentiment_score": lead.avg_sentiment_score,
            "conversation_count": lead.conversation_count,
            "recency_score": lead.recency_score,
        }
    except HTTPException:
        # pass through HTTP errors as-is
        raise
    except Exception as exc:
        traceback.print_exc()
        # Surface the exception message in the response for debugging
        raise HTTPException(status_code=500, detail=f"conversation_error: {exc}")
