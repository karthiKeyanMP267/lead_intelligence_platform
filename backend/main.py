from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json
from pathlib import Path

try:
    from database import engine, Base, SessionLocal
    from models import Lead
    from retrain import retrain_model
    from inference import score_all_leads, assign_priorities
    from inference import score_single_lead
except ModuleNotFoundError:
    from database import engine, Base, SessionLocal
    from models import Lead
    from inference import score_all_leads, assign_priorities
    from inference import score_single_lead

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)


# -----------------------------
# Database Dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/")
def read_root():
    return {"message": "Backend running successfully"}


# -----------------------------
# Get Leads (sorted by score)
# -----------------------------
@app.get("/leads")
def get_leads(limit: int = 100, db: Session = Depends(get_db)):
    leads = (
        db.query(Lead)
        .order_by(Lead.score.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "lead_id": lead.lead_id,
            "industry": lead.industry,
            "annual_revenue": lead.annual_revenue,
            "country": lead.country,
            "score": lead.score,
            "priority": lead.priority
        }
        for lead in leads
    ]


# -----------------------------
# Get Model Metrics
# -----------------------------
@app.get("/metrics")
def get_metrics():
    metrics_path = MODELS_DIR / "metrics.json"
    if metrics_path.exists():
        with open(metrics_path) as f:
            return json.load(f)
    return {"error": "Metrics not found"}


# -----------------------------
# Get Feature Importance
# -----------------------------
@app.get("/feature-importance")
def get_feature_importance():
    feature_importance_path = MODELS_DIR / "feature_importance.json"
    if feature_importance_path.exists():
        with open(feature_importance_path) as f:
            return json.load(f)
    return {"error": "Feature importance not found"}


# -----------------------------
# Batch Score Endpoint
# -----------------------------
@app.post("/batch-score")
def batch_score():
    score_all_leads()
    assign_priorities()
    return {"message": "Batch scoring and priority assignment completed"}

@app.post("/simulate-event/{lead_id}")
def simulate_event(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.lead_id == lead_id).first()

    if not lead:
        return {"error": "Lead not found"}

    # Simulate engagement
    lead.website_visits += 2
    lead.email_clicks += 1
    lead.days_since_last_activity = 0

    db.commit()

    # Re-score this lead
    new_score = score_single_lead(lead_id)

    # Reassign priority after scoring
    assign_priorities()

    return {
        "message": "Event simulated and lead re-scored",
        "new_score": new_score
    }

@app.post("/retrain")
def retrain():
    metrics = retrain_model()
    score_all_leads()
    assign_priorities()
    return {
        "message": "Model retrained and leads re-scored",
        "metrics": metrics
    }