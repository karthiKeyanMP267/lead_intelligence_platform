import pandas as pd
import numpy as np
import os
from pathlib import Path

np.random.seed(42)
n = 20000

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

industries = ["SaaS", "Finance", "Healthcare", "Retail", "Manufacturing"]
countries = ["India", "USA", "UK", "Germany", "Singapore"]
lead_stages = ["New", "Contacted", "Qualified", "Proposal"]
sources = ["Google Ads", "LinkedIn", "Referral", "Organic"]

# CRM DATA
crm_data = pd.DataFrame({
    "lead_id": range(1, n + 1),
    "industry": np.random.choice(industries, n),
    "company_size": np.random.randint(10, 1000, n),
    "annual_revenue": np.random.randint(100000, 5000000, n),
    "country": np.random.choice(countries, n),
    "lead_stage": np.random.choice(lead_stages, n, p=[0.4,0.3,0.2,0.1]),
    "previous_interactions": np.random.randint(0, 15, n)
})

# ACTIVITY DATA
activity_data = pd.DataFrame({
    "lead_id": range(1, n + 1),
    "website_visits": np.random.randint(1, 50, n),
    "pages_viewed": np.random.randint(1, 25, n),
    "email_clicks": np.random.randint(0, 20, n),
    "calls_made": np.random.randint(0, 10, n),
    "meetings_scheduled": np.random.randint(0, 5, n),
    "demo_requested": np.random.choice([0,1], n, p=[0.7,0.3]),
    "time_spent_minutes": np.random.randint(1, 300, n),
    "days_since_last_activity": np.random.randint(0, 60, n)
})

# MARKETING DATA
marketing_data = pd.DataFrame({
    "lead_id": range(1, n + 1),
    "source": np.random.choice(sources, n),
    "ads_clicked": np.random.randint(0, 10, n),
    "campaign_engagement_score": np.random.uniform(0, 1, n)
})

crm_data.to_csv(RAW_DATA_DIR / "crm_leads.csv", index=False)
activity_data.to_csv(RAW_DATA_DIR / "activity_logs.csv", index=False)
marketing_data.to_csv(RAW_DATA_DIR / "marketing_data.csv", index=False)

print("Raw multi-source data generated successfully.")