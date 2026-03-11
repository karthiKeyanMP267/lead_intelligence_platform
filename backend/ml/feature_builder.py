def build_feature_vector(lead):
    """Build ordered feature vector for a single lead including conversation signals."""
    return [[
        lead.email_clicks or 0,
        lead.website_visits or 0,
        lead.engagement_count if hasattr(lead, "engagement_count") else getattr(lead, "previous_interactions", 0) or 0,
        lead.avg_sentiment_score or 0.0,
        lead.avg_intent_score or 0.0,
        lead.avg_urgency_score or 0.0,
        lead.conversation_count or 0,
        lead.recency_score if lead.recency_score is not None else 1.0,
    ]]
