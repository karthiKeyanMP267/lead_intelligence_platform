import pandas as pd
import numpy as np
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

crm = pd.read_csv(RAW_DATA_DIR / "crm_leads.csv")
activity = pd.read_csv(RAW_DATA_DIR / "activity_logs.csv")
marketing = pd.read_csv(RAW_DATA_DIR / "marketing_data.csv")

# Merge
data = crm.merge(activity, on="lead_id")
data = data.merge(marketing, on="lead_id")

# Business score formula
score = (
    0.0000002 * data["annual_revenue"] +
    0.02 * data["website_visits"] +
    0.03 * data["email_clicks"] +
    0.05 * data["pages_viewed"] +
    0.3 * data["demo_requested"] +
    0.02 * data["previous_interactions"] +
    -0.02 * data["days_since_last_activity"] +
    0.1 * data["campaign_engagement_score"] +
    0.00000005 * data["annual_revenue"] * data["demo_requested"] +
    0.01 * data["email_clicks"] * data["website_visits"]
)

# Normalize to 0–1
# Normalize to 0–1
score = (score - score.min()) / (score.max() - score.min())

# Add moderate noise (not too much)
noise = np.random.normal(0, 0.08, len(score))

probability = np.clip(score + noise, 0, 1)

# Instead of shrinking, use percentile to anchor class balance
threshold = np.percentile(probability, 70)

data["converted"] = (probability > threshold).astype(int)

data.to_csv(PROCESSED_DATA_DIR / "consolidated_leads.csv", index=False)

print("Data consolidated and target created.")
print("Conversion Rate:", data["converted"].mean())