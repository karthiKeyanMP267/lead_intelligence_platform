import joblib
import pandas as pd
from pathlib import Path

try:
    from backend.database import SessionLocal
    from backend.models import Lead
except ModuleNotFoundError:
    from database import SessionLocal
    from models import Lead

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "best_model.pkl"

# Load trained model
model = joblib.load(MODEL_PATH)


def score_single_lead(lead_id):
    db = SessionLocal()

    lead = db.query(Lead).filter(Lead.lead_id == lead_id).first()

    if not lead:
        db.close()
        return None

    # Convert to DataFrame
    data = pd.DataFrame([{
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
        "campaign_engagement_score": lead.campaign_engagement_score
    }])

    data = pd.get_dummies(data, drop_first=True)

    model_features = model.get_booster().feature_names

    for col in model_features:
        if col not in data.columns:
            data[col] = 0

    data = data[model_features]

    score = float(model.predict_proba(data)[:, 1][0])

    lead.score = float(score)

    db.commit()
    db.close()

    return score

def score_all_leads():
    db = SessionLocal()

    leads = db.query(Lead).all()

    if not leads:
        print("No leads found.")
        return

    # Convert DB rows → DataFrame
    data = []
    for lead in leads:
        data.append({
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
            "campaign_engagement_score": lead.campaign_engagement_score
        })

    df = pd.DataFrame(data)

    # Apply same preprocessing used during training
    df = pd.get_dummies(df, drop_first=True)

    # IMPORTANT: Align columns with training
    model_features = model.get_booster().feature_names
    for col in model_features:
        if col not in df.columns:
            df[col] = 0

    df = df[model_features]

    # Predict probabilities
    scores = model.predict_proba(df)[:, 1]

    # Update DB
    for lead, score in zip(leads, scores):
        lead.score = float(score)

    db.commit()
    db.close()

    print("Scoring completed.")

def assign_priorities():
    db = SessionLocal()

    leads = db.query(Lead).order_by(Lead.score.desc()).all()

    total = len(leads)

    if total == 0:
        print("No leads to assign priority.")
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
    db.close()

    print("Priority assignment completed.")


if __name__ == "__main__":
    score_all_leads()
    assign_priorities()