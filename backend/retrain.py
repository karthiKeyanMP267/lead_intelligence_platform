import pandas as pd
import joblib
import json
from pathlib import Path
import sys
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
from xgboost import XGBClassifier

try:
    from backend.database import SessionLocal
    from backend.models import Lead
    from backend.inference import reload_model
except ModuleNotFoundError:
    from database import SessionLocal
    from models import Lead
    from inference import reload_model

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "best_model.pkl"
METRICS_PATH = BASE_DIR / "models" / "metrics.json"
FEATURES_PATH = BASE_DIR / "models" / "feature_columns.json"

# Minimum number of labelled leads required before retraining
MIN_SAMPLES = 30


def retrain_model() -> dict:
    db = SessionLocal()
    try:
        leads = db.query(Lead).filter(Lead.converted.isnot(None)).all()

        if len(leads) < MIN_SAMPLES:
            return {
                "error": f"Need at least {MIN_SAMPLES} labelled leads to retrain. "
                         f"Currently have {len(leads)}."
            }

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
                "avg_sentiment_score": getattr(lead, "avg_sentiment_score", 0.0) or 0.0,
                "avg_intent_score": getattr(lead, "avg_intent_score", 0.0) or 0.0,
                "avg_urgency_score": getattr(lead, "avg_urgency_score", 0.0) or 0.0,
                "conversation_count": getattr(lead, "conversation_count", 0) or 0,
                "recency_score": getattr(lead, "recency_score", 1.0) if getattr(lead, "recency_score", None) is not None else 1.0,
                "converted": lead.converted,
            })

        df = pd.DataFrame(data)
        y = df.pop("converted")
        X = pd.get_dummies(df, drop_first=True)

        # Save feature column order so inference always aligns correctly
        feature_columns = X.columns.tolist()
        with open(FEATURES_PATH, "w") as f:
            json.dump(feature_columns, f)

        # Train / test split for honest evaluation
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        new_model = XGBClassifier(
            n_estimators=300,
            max_depth=4,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            eval_metric="logloss",
        )
        new_model.fit(X_train, y_train)

        y_pred = new_model.predict(X_test)
        y_prob = new_model.predict_proba(X_test)[:, 1]

        metrics = {
            "XGBoost_Retrained": {
                "precision": float(precision_score(y_test, y_pred, zero_division=0)),
                "recall": float(recall_score(y_test, y_pred, zero_division=0)),
                "f1": float(f1_score(y_test, y_pred, zero_division=0)),
                "auc": float(roc_auc_score(y_test, y_prob)),
                "samples_used": len(leads),
            }
        }

        # Persist new model + metrics
        joblib.dump(new_model, MODEL_PATH)
        with open(METRICS_PATH, "w") as f:
            json.dump(metrics, f, indent=4)

        # Hot-reload the new model into the inference module
        reload_model()

        print(f"[retrain] Retraining complete. AUC = {metrics['XGBoost_Retrained']['auc']:.4f}")
        return metrics

    finally:
        db.close()


def _print_result(result: dict):
    """Pretty-print retrain results and set an exit code for CLI use."""
    # If an error key is present, surface it and exit non-zero so scripts can fail fast.
    if "error" in result:
        print(f"[retrain] {result['error']}")
        sys.exit(1)

    # Happy path: show the metrics summary.
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    outcome = retrain_model()
    _print_result(outcome)
