from fastapi import FastAPI, Depends, BackgroundTasks, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import json
import io
import threading
import pandas as pd
from pathlib import Path

try:
    from database import engine, Base, SessionLocal
    from models import Lead
    from retrain import retrain_model
    from inference import score_all_leads, assign_priorities, score_single_lead, score_lead_payload
    from routes.conversation import router as conversation_router
    from schemas import LeadCreate, LeadUpdate
except ModuleNotFoundError:
    from database import engine, Base, SessionLocal
    from models import Lead
    from retrain import retrain_model
    from inference import score_all_leads, assign_priorities, score_single_lead, score_lead_payload
    from routes.conversation import router as conversation_router
    from schemas import LeadCreate, LeadUpdate

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

# ---------------------------------------------------------------------------
# Auto-retrain configuration
# ---------------------------------------------------------------------------
# Trigger a full retrain every time this many new leads have been ingested.
RETRAIN_THRESHOLD: int = 1000
_counter_lock = threading.Lock()
_new_leads_count: int = 0          # leads ingested since the last retrain
_retrain_in_progress: bool = False  # guard against concurrent retrains


def _background_retrain():
    """Run retrain + re-score in a background thread, then reset the counter."""
    global _new_leads_count, _retrain_in_progress
    try:
        print("[auto-retrain] Starting automatic retraining...")
        retrain_model()
        score_all_leads()
        assign_priorities()
        print("[auto-retrain] Done — model updated and leads re-scored.")
    finally:
        with _counter_lock:
            _new_leads_count = 0
            _retrain_in_progress = False


def _maybe_trigger_retrain(background_tasks: BackgroundTasks, count: int = 1):
    """Increment the ingestion counter and schedule a retrain when the threshold is hit."""
    global _new_leads_count, _retrain_in_progress
    with _counter_lock:
        _new_leads_count += count
        should_retrain = (
            _new_leads_count >= RETRAIN_THRESHOLD and not _retrain_in_progress
        )
        if should_retrain:
            _retrain_in_progress = True
    if should_retrain:
        print(f"[auto-retrain] Threshold reached ({_new_leads_count} new leads). Scheduling retrain.")
        background_tasks.add_task(_background_retrain)

# CORS: use explicit origins to satisfy browser + credentials rules
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(conversation_router)

# Create tables (and backfill new columns for existing deployments)
Base.metadata.create_all(bind=engine)


def _ensure_conversation_columns():
    """Add conversation feature columns if the table pre-exists without them.

    This is idempotent and safe to run at startup.
    """
    ddl = [
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS avg_sentiment_score FLOAT DEFAULT 0",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS avg_intent_score FLOAT DEFAULT 0",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS avg_urgency_score FLOAT DEFAULT 0",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS conversation_count INT DEFAULT 0",
        "ALTER TABLE leads ADD COLUMN IF NOT EXISTS recency_score FLOAT DEFAULT 1",
    ]
    with engine.connect() as conn:
        for stmt in ddl:
            conn.execute(text(stmt))
        conn.commit()


_ensure_conversation_columns()


@app.on_event("startup")
def _bootstrap_scores():
    """If scores are missing (fresh load), score all leads and assign priorities."""
    db = SessionLocal()
    try:
        missing = db.query(Lead).filter(Lead.score.is_(None)).limit(1).first()
        if missing:
            print("[startup] Found leads without scores. Scoring all leads...")
            score_all_leads()
            assign_priorities()
            print("[startup] Initial scoring complete.")
    finally:
        db.close()


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
def get_leads(limit: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Lead).order_by(Lead.score.desc())
    if limit is not None and limit > 0:
        query = query.limit(limit)
    leads = query.all()

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


@app.get("/leads/{lead_id}")
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.lead_id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    return {
        "lead_id": lead.lead_id,
        "industry": lead.industry,
        "company_size": lead.company_size,
        "annual_revenue": lead.annual_revenue,
        "country": lead.country,
        "lead_stage": lead.lead_stage,
        "previous_interactions": lead.previous_interactions,
        "website_visits": lead.website_visits,
        "pages_viewed": lead.pages_viewed,
        "email_clicks": lead.email_clicks,
        "calls_made": lead.calls_made,
        "meetings_scheduled": lead.meetings_scheduled,
        "demo_requested": lead.demo_requested,
        "time_spent_minutes": lead.time_spent_minutes,
        "days_since_last_activity": lead.days_since_last_activity,
        "source": lead.source,
        "ads_clicked": lead.ads_clicked,
        "campaign_engagement_score": lead.campaign_engagement_score,
        "converted": lead.converted,
        "score": lead.score,
        "priority": lead.priority,
    }


@app.put("/leads/{lead_id}")
def update_lead(lead_id: int, lead_data: LeadUpdate, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.lead_id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    changes = lead_data.dict(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    for field, value in changes.items():
        setattr(lead, field, value)

    db.commit()

    # Re-score this same lead and re-assign overall priorities
    new_score = score_single_lead(lead_id)
    assign_priorities()

    db.refresh(lead)
    return {
        "message": "Lead updated and re-scored",
        "lead_id": lead.lead_id,
        "score": float(new_score) if new_score is not None else lead.score,
        "priority": lead.priority,
    }


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


@app.post("/predict/lead")
def predict_lead(lead_data: LeadCreate):
    payload = {
        "industry": lead_data.industry,
        "company_size": lead_data.company_size,
        "annual_revenue": lead_data.annual_revenue,
        "country": lead_data.country,
        "lead_stage": lead_data.lead_stage,
        "previous_interactions": lead_data.previous_interactions,
        "website_visits": lead_data.website_visits,
        "pages_viewed": lead_data.pages_viewed,
        "email_clicks": lead_data.email_clicks,
        "calls_made": lead_data.calls_made,
        "meetings_scheduled": lead_data.meetings_scheduled,
        "demo_requested": lead_data.demo_requested,
        "time_spent_minutes": lead_data.time_spent_minutes,
        "days_since_last_activity": lead_data.days_since_last_activity,
        "source": lead_data.source,
        "ads_clicked": lead_data.ads_clicked,
        "campaign_engagement_score": lead_data.campaign_engagement_score,
    }
    score = score_lead_payload(payload)
    return {"predicted_score": score}


# -----------------------------
# Ingest a single lead (JSON)
# -----------------------------
@app.post("/ingest/lead", status_code=201)
def ingest_lead(
    lead_data: LeadCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Accept one lead, score it immediately with the current model,
    then auto-retrain in the background when the threshold is reached."""
    try:
        # Keep PK sequence in sync (important after bulk/manual seed loads)
        db.execute(
            text(
                "SELECT setval(pg_get_serial_sequence('leads','lead_id'), "
                "COALESCE((SELECT MAX(lead_id) FROM leads), 1), true)"
            )
        )
        db.commit()

        new_lead = Lead(
            industry=lead_data.industry,
            company_size=lead_data.company_size,
            annual_revenue=lead_data.annual_revenue,
            country=lead_data.country,
            lead_stage=lead_data.lead_stage,
            previous_interactions=lead_data.previous_interactions,
            website_visits=lead_data.website_visits,
            pages_viewed=lead_data.pages_viewed,
            email_clicks=lead_data.email_clicks,
            calls_made=lead_data.calls_made,
            meetings_scheduled=lead_data.meetings_scheduled,
            demo_requested=lead_data.demo_requested,
            time_spent_minutes=lead_data.time_spent_minutes,
            days_since_last_activity=lead_data.days_since_last_activity,
            source=lead_data.source,
            ads_clicked=lead_data.ads_clicked,
            campaign_engagement_score=lead_data.campaign_engagement_score,
            converted=lead_data.converted,
            score=None,
            priority=None,
        )
        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)

        # Immediately score this lead with the live model
        score = score_single_lead(new_lead.lead_id)
        assign_priorities()

        # Maybe trigger a background retrain
        _maybe_trigger_retrain(background_tasks, count=1)

        return {
            "message": "Lead ingested and scored",
            "lead_id": new_lead.lead_id,
            "score": score,
            "auto_retrain_in": max(0, RETRAIN_THRESHOLD - _new_leads_count),
        }
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to ingest lead")


# -----------------------------
# Ingest leads from a CSV file
# -----------------------------
@app.post("/ingest/csv", status_code=201)
async def ingest_csv(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a CSV of leads, bulk-insert them, re-score everything,
    then auto-retrain in the background when the threshold is reached."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted.")

    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    required_cols = {
        "industry", "company_size", "annual_revenue", "country", "lead_stage",
        "previous_interactions", "website_visits", "pages_viewed", "email_clicks",
        "calls_made", "meetings_scheduled", "demo_requested", "time_spent_minutes",
        "days_since_last_activity", "source", "ads_clicked", "campaign_engagement_score",
    }
    missing = required_cols - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"CSV is missing required columns: {sorted(missing)}",
        )

    BATCH_SIZE = 1000
    total_inserted = 0

    for start in range(0, len(df), BATCH_SIZE):
        chunk = df.iloc[start:start + BATCH_SIZE]
        batch = []
        for _, row in chunk.iterrows():
            batch.append(Lead(
                industry=row["industry"],
                company_size=int(row["company_size"]),
                annual_revenue=float(row["annual_revenue"]),
                country=row["country"],
                lead_stage=row["lead_stage"],
                previous_interactions=int(row["previous_interactions"]),
                website_visits=int(row["website_visits"]),
                pages_viewed=int(row["pages_viewed"]),
                email_clicks=int(row["email_clicks"]),
                calls_made=int(row["calls_made"]),
                meetings_scheduled=int(row["meetings_scheduled"]),
                demo_requested=int(row["demo_requested"]),
                time_spent_minutes=int(row["time_spent_minutes"]),
                days_since_last_activity=int(row["days_since_last_activity"]),
                source=row["source"],
                ads_clicked=int(row["ads_clicked"]),
                campaign_engagement_score=float(row["campaign_engagement_score"]),
                converted=int(row["converted"]) if "converted" in row and pd.notna(row["converted"]) else 0,
                score=None,
                priority=None,
            ))
        db.bulk_save_objects(batch)
        db.commit()
        total_inserted += len(batch)

    # Re-score and re-prioritise all leads
    score_all_leads()
    assign_priorities()

    # Maybe trigger a background retrain
    _maybe_trigger_retrain(background_tasks, count=total_inserted)

    return {
        "message": f"{total_inserted} leads ingested and scored",
        "count": total_inserted,
        "batch_size": BATCH_SIZE,
        "auto_retrain_in": max(0, RETRAIN_THRESHOLD - _new_leads_count),
    }


# -----------------------------
# Ingestion status
# -----------------------------
@app.get("/ingest/status")
def ingest_status():
    """How many new leads until the next automatic retrain."""
    return {
        "new_leads_since_last_retrain": _new_leads_count,
        "retrain_threshold": RETRAIN_THRESHOLD,
        "retrain_in_progress": _retrain_in_progress,
        "leads_until_next_retrain": max(0, RETRAIN_THRESHOLD - _new_leads_count),
    }