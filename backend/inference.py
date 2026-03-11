import joblib
import pandas as pd
import json
import threading
from pathlib import Path

try:
    from backend.database import SessionLocal
    from backend.models import Lead
except ModuleNotFoundError:
    from database import SessionLocal
    from models import Lead

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "best_model.pkl"
FEATURES_PATH = BASE_DIR / "models" / "feature_columns.json"

# Thread-safe model container
_model_lock = threading.Lock()
model = joblib.load(MODEL_PATH)


def reload_model():
    """Hot-reload the model from disk after retraining (thread-safe)."""
    global model
    with _model_lock:
        model = joblib.load(MODEL_PATH)
    print("[inference] Model reloaded from disk.")


def _get_feature_columns():
    """Return the feature column list saved during the last training run."""
    if FEATURES_PATH.exists():
        with open(FEATURES_PATH) as f:
            return json.load(f)
    # Fallback for legacy models saved before feature_columns.json existed
    with _model_lock:
        if hasattr(model, "get_booster"):
            return list(model.get_booster().feature_names)
        if hasattr(model, "feature_names_in_"):
            return list(model.feature_names_in_)
        if hasattr(model, "named_steps") and "lr" in model.named_steps:
            lr_step = model.named_steps["lr"]
            if hasattr(lr_step, "feature_names_in_"):
                return list(lr_step.feature_names_in_)
    raise RuntimeError("Unable to infer model feature columns. Run /retrain once to generate models/feature_columns.json.")


def _lead_to_dict(lead) -> dict:
    return {
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
        "avg_sentiment_score": getattr(lead, "avg_sentiment_score", 0.0) or 0.0,
        "avg_intent_score": getattr(lead, "avg_intent_score", 0.0) or 0.0,
        "avg_urgency_score": getattr(lead, "avg_urgency_score", 0.0) or 0.0,
        "conversation_count": getattr(lead, "conversation_count", 0) or 0,
        "recency_score": getattr(lead, "recency_score", 1.0) if getattr(lead, "recency_score", None) is not None else 1.0,
    }


def _prepare_df(df: pd.DataFrame) -> pd.DataFrame:
    """One-hot encode then align columns exactly to the training feature set."""
    df = pd.get_dummies(df, drop_first=True)
    feature_cols = _get_feature_columns()
    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0
    return df[feature_cols]


def score_lead_payload(payload: dict) -> float:
    """Score a lead payload directly (without writing to DB)."""
    data = pd.DataFrame([payload])
    data = _prepare_df(data)
    with _model_lock:
        return float(model.predict_proba(data)[:, 1][0])


def score_lead_instance(lead: Lead) -> float:
    """Score an in-memory Lead instance without re-querying the DB."""
    data = pd.DataFrame([_lead_to_dict(lead)])
    data = _prepare_df(data)
    with _model_lock:
        return float(model.predict_proba(data)[:, 1][0])


# -----------------------------------------------------------------------
# Score a single lead by lead_id
# -----------------------------------------------------------------------
def score_single_lead(lead_id: int):
    db = SessionLocal()
    try:
        lead = db.query(Lead).filter(Lead.lead_id == lead_id).first()
        if not lead:
            return None

        score = score_lead_instance(lead)
        lead.score = score
        db.commit()
        return score
    finally:
        db.close()


# -----------------------------------------------------------------------
# Score all leads in the database
# -----------------------------------------------------------------------
def score_all_leads():
    db = SessionLocal()
    try:
        leads = db.query(Lead).all()
        if not leads:
            print("[inference] No leads found.")
            return

        df = pd.DataFrame([_lead_to_dict(l) for l in leads])
        df = _prepare_df(df)

        with _model_lock:
            scores = model.predict_proba(df)[:, 1]

        for lead, score in zip(leads, scores):
            lead.score = float(score)

        db.commit()
        print(f"[inference] Scored {len(leads)} leads.")
    finally:
        db.close()


# -----------------------------------------------------------------------
# Assign HOT / WARM / COLD priorities based on score percentiles
# -----------------------------------------------------------------------
def assign_priorities():
    db = SessionLocal()
    try:
        leads = db.query(Lead).order_by(Lead.score.desc()).all()
        total = len(leads)

        if total == 0:
            print("[inference] No leads to assign priority.")
            return

        for index, lead in enumerate(leads):
            percentile = index / total
            if percentile <= 0.2:
                lead.priority = "HOT"
            elif percentile <= 0.5:
                lead.priority = "WARM"
            else:
                lead.priority = "COLD"

        db.commit()
        print("[inference] Priority assignment completed.")
    finally:
        db.close()


if __name__ == "__main__":
    score_all_leads()
    assign_priorities()