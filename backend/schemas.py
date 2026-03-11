from pydantic import BaseModel
from typing import Optional


class ConversationRequest(BaseModel):
    text: str


class LeadCreate(BaseModel):
    industry: str
    company_size: int
    annual_revenue: float
    country: str
    lead_stage: str
    previous_interactions: int
    website_visits: int
    pages_viewed: int
    email_clicks: int
    calls_made: int
    meetings_scheduled: int
    demo_requested: int
    time_spent_minutes: int
    days_since_last_activity: int
    source: str
    ads_clicked: int
    campaign_engagement_score: float
    converted: Optional[int] = 0


class LeadUpdate(BaseModel):
    industry: Optional[str] = None
    company_size: Optional[int] = None
    annual_revenue: Optional[float] = None
    country: Optional[str] = None
    lead_stage: Optional[str] = None
    previous_interactions: Optional[int] = None
    website_visits: Optional[int] = None
    pages_viewed: Optional[int] = None
    email_clicks: Optional[int] = None
    calls_made: Optional[int] = None
    meetings_scheduled: Optional[int] = None
    demo_requested: Optional[int] = None
    time_spent_minutes: Optional[int] = None
    days_since_last_activity: Optional[int] = None
    source: Optional[str] = None
    ads_clicked: Optional[int] = None
    campaign_engagement_score: Optional[float] = None
    converted: Optional[int] = None
