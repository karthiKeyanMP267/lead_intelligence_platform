import pandas as pd
import joblib
import json
import os
from sqlalchemy.orm import Session
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
from xgboost import XGBClassifier
from backend.database import SessionLocal
from backend.models import Lead

MODEL_PATH = "models/best_model.pkl"

def retrain_model():
    db: Session = SessionLocal()

    leads = db.query(Lead).all()

    if not leads:
        db.close()
        return {"error": "No data available for retraining"}

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
            "campaign_engagement_score": lead.campaign_engagement_score,
            "converted": lead.converted
        })

    df = pd.DataFrame(data)

    y = df["converted"]
    X = df.drop(columns=["converted"])

    X = pd.get_dummies(X, drop_first=True)

    model = XGBClassifier(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )

    model.fit(X, y)

    # Evaluate
    y_pred = model.predict(X)
    y_prob = model.predict_proba(X)[:, 1]

    metrics = {
        "precision": float(precision_score(y, y_pred)),
        "recall": float(recall_score(y, y_pred)),
        "f1": float(f1_score(y, y_pred)),
        "auc": float(roc_auc_score(y, y_prob))
    }

    joblib.dump(model, MODEL_PATH)

    with open("models/metrics.json", "w") as f:
        json.dump({"XGBoost_Retrained": metrics}, f, indent=4)

    db.close()

    return metrics