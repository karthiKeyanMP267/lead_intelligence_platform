from transformers import pipeline
import re

# Load once at startup
zero_shot = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli"
)

sentiment_model = pipeline("sentiment-analysis")

# Semantic label set to reduce brittleness and rely on semantic mapping
INTENT_LABELS = [
    "explicit rejection",
    "competitor chosen",
    "temporary no but future possible",
    "budget constraint",
    "timeline constraint",
    "compliance or security concern",
    "technical validation required",
    "freezing spend",
    "procurement blocked",
    "deprioritized initiative",
    "renewal risk",
    "pilot requested",
    "expansion opportunity",
    "support request",
    "requesting pricing",
    "ready to purchase",
    "purchase approved",
    "neutral inquiry",
]


def analyze_conversation(text: str):
    """Extract semantic intent/urgency and sentiment without rule multipliers."""

    intent_result = zero_shot(text, INTENT_LABELS)
    scores = dict(zip(intent_result["labels"], intent_result["scores"]))

    lowered = text.lower().replace("’", "'")
    normalized = re.sub(r"[^a-z0-9\s]", " ", lowered)

    unsubscribe_terms = ["unsubscribe", "opt out", "remove me"]
    spam_terms = ["buy followers", "free money", "lottery"]

    def _contains_any(terms):
        return any(term in lowered or term in normalized for term in terms)

    # Base sentiment
    sentiment = sentiment_model(text)[0]
    sentiment_score = sentiment["score"]
    if sentiment["label"] == "NEGATIVE":
        sentiment_score = -sentiment_score

    rejection_prob = scores.get("explicit rejection", 0.0)
    competitor_prob = scores.get("competitor chosen", 0.0)
    budget_prob = scores.get("budget constraint", 0.0)
    timeline_prob = scores.get("timeline constraint", 0.0)
    compliance_prob = scores.get("compliance or security concern", 0.0)
    technical_prob = scores.get("technical validation required", 0.0)
    spend_prob = scores.get("freezing spend", 0.0)
    procurement_prob = scores.get("procurement blocked", 0.0)
    deprioritize_prob = scores.get("deprioritized initiative", 0.0)
    renewal_prob = scores.get("renewal risk", 0.0)
    pilot_prob = scores.get("pilot requested", 0.0)
    expansion_prob = scores.get("expansion opportunity", 0.0)
    support_prob = scores.get("support request", 0.0)
    pricing_prob = scores.get("requesting pricing", 0.0)
    ready_prob = scores.get("ready to purchase", 0.0)
    approved_prob = scores.get("purchase approved", 0.0)
    neutral_prob = scores.get("neutral inquiry", 0.0)

    # Derive intent/urgency directly from semantic buckets (no clamping/floors)
    intent_score = max(
        ready_prob,
        approved_prob,
        pricing_prob * 0.8,
        expansion_prob * 0.6,
        pilot_prob * 0.5,
        neutral_prob * 0.2,
        0.0,
    )

    urgency_score = max(
        pricing_prob,
        ready_prob,
        approved_prob,
        pilot_prob * 0.65,
        timeline_prob * 0.7,
        budget_prob * 0.4,
        spend_prob * 0.5,
        procurement_prob * 0.5,
        expansion_prob * 0.45,
        support_prob * 0.3,
        0.0,
    )

    # Minimal guardrail for legal unsubscribe/spam only
    if _contains_any(spam_terms) or _contains_any(unsubscribe_terms) or max(rejection_prob, competitor_prob) >= 0.9:
        intent_score = 0.0
        urgency_score = 0.0
        sentiment_score = min(sentiment_score, -0.9)

    # Clamp sentiment to [-1, 1]
    sentiment_score = max(min(sentiment_score, 1.0), -1.0)

    return {
        "intent_score": intent_score,
        "urgency_score": urgency_score,
        "sentiment_score": sentiment_score,
    }
