from sqlalchemy import Column, Integer, Float, String

try:
    from backend.database import Base
except ModuleNotFoundError:
    from database import Base

class Lead(Base):
    __tablename__ = "leads"

    lead_id = Column(Integer, primary_key=True, index=True)

    industry = Column(String)
    company_size = Column(Integer)
    annual_revenue = Column(Float)
    country = Column(String)
    lead_stage = Column(String)
    previous_interactions = Column(Integer)

    website_visits = Column(Integer)
    pages_viewed = Column(Integer)
    email_clicks = Column(Integer)
    calls_made = Column(Integer)
    meetings_scheduled = Column(Integer)
    demo_requested = Column(Integer)
    time_spent_minutes = Column(Integer)
    days_since_last_activity = Column(Integer)

    source = Column(String)
    ads_clicked = Column(Integer)
    campaign_engagement_score = Column(Float)

    # Aggregated conversation/NLP signals
    avg_sentiment_score = Column(Float, default=0.0)
    avg_intent_score = Column(Float, default=0.0)
    avg_urgency_score = Column(Float, default=0.0)
    conversation_count = Column(Integer, default=0)
    recency_score = Column(Float, default=1.0)

    score = Column(Float)
    priority = Column(String)
    converted = Column(Integer)