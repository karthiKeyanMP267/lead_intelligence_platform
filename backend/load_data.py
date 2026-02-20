import pandas as pd
from sqlalchemy.orm import Session
from pathlib import Path

try:
    from backend.database import SessionLocal
    from backend.models import Lead
except ModuleNotFoundError:
    from database import SessionLocal
    from models import Lead

BASE_DIR = Path(__file__).resolve().parent
CONSOLIDATED_DATA_PATH = BASE_DIR / "data" / "processed" / "consolidated_leads.csv"

# Load consolidated CSV
df = pd.read_csv(CONSOLIDATED_DATA_PATH)

def load_data():
    db: Session = SessionLocal()

    # Clear existing data (optional for now)
    db.query(Lead).delete()
    db.commit()

    leads = []

    for _, row in df.iterrows():
        lead = Lead(
            lead_id=int(row["lead_id"]),
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
            converted=int(row["converted"]),    
            score=None,
            priority=None
        )
        leads.append(lead)

    db.bulk_save_objects(leads)
    db.commit()
    db.close()

    print("Data successfully loaded into PostgreSQL!")

if __name__ == "__main__":
    load_data()