def update_conversation_features(lead, new_features, alpha: float = 0.6):
    """Update conversation aggregates using pure EMA; no rule clamps."""

    def ema(prev, new):
        return alpha * new + (1 - alpha) * (prev if prev is not None else 0.0)

    intent_in = new_features["intent_score"]
    urgency_in = new_features["urgency_score"]
    sentiment_in = new_features["sentiment_score"]

    lead.avg_intent_score = ema(lead.avg_intent_score, intent_in)
    lead.avg_urgency_score = ema(lead.avg_urgency_score, urgency_in)
    lead.avg_sentiment_score = ema(lead.avg_sentiment_score, sentiment_in)

    lead.conversation_count = (lead.conversation_count or 0) + 1
    lead.recency_score = 0.0
