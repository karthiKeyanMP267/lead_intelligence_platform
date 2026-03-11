import pandas as pd
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Conversation synthesis with correlation to conversion propensity
# ---------------------------------------------------------------------------
TEMPLATES = [
    {
        "name": "high_intent",
        "sentiment": 0.82,
        "intent": 0.9,
        "urgency": 0.9,
    },
    {
        "name": "pricing",
        "sentiment": 0.55,
        "intent": 0.7,
        "urgency": 0.85,
    },
    {
        "name": "technical",
        "sentiment": 0.42,
        "intent": 0.55,
        "urgency": 0.5,
    },
    {
        "name": "objection",
        "sentiment": -0.35,
        "intent": 0.25,
        "urgency": 0.45,
    },
    {
        "name": "low_engagement",
        "sentiment": 0.05,
        "intent": 0.1,
        "urgency": 0.1,
    },
    {
        "name": "opt_out",
        "sentiment": -0.6,
        "intent": 0.05,
        "urgency": 0.05,
    },
]


def _pick_template(probability: float) -> dict:
    """Sample a template with weights driven by the latent conversion propensity."""
    p = float(np.clip(probability, 0.0, 1.0))

    weights = {
        "high_intent": 0.05 + 0.55 * p,
        "pricing": 0.10 + 0.30 * p,
        "technical": 0.15,
        "objection": 0.10 + 0.35 * (1 - p),
        "low_engagement": 0.25 + 0.35 * (1 - p),
        "opt_out": 0.10 + 0.20 * (1 - p),
    }

    names = list(weights.keys())
    probs = np.array([weights[n] for n in names], dtype=float)
    probs = probs / probs.sum()
    chosen = np.random.choice(names, p=probs)
    return next(t for t in TEMPLATES if t["name"] == chosen)


def _sample_conversation_features(probability: float, max_count: int = 6):
    """Generate aggregated convo features conditioned on propensity."""
    template = _pick_template(probability)

    # More engaged leads tend to have more interactions
    lam = 0.5 + 1.5 * probability
    convo_count = int(np.clip(np.random.poisson(lam=lam), 0, max_count))

    if convo_count == 0:
        return {
            "avg_sentiment_score": 0.0,
            "avg_intent_score": 0.0,
            "avg_urgency_score": 0.0,
            "conversation_count": 0,
            "recency_score": 1.0,
        }

    def noisy(val, sd):
        return float(np.clip(np.random.normal(val, sd), -1.0, 1.0))

    sentiments = [noisy(template["sentiment"], 0.08) for _ in range(convo_count)]
    intents = [float(np.clip(np.random.normal(template["intent"], 0.05), 0.0, 1.0)) for _ in range(convo_count)]
    urgencies = [float(np.clip(np.random.normal(template["urgency"], 0.07), 0.0, 1.0)) for _ in range(convo_count)]

    # Higher propensity → more recent contact (lower recency_score)
    a_param = 2 + 3 * probability
    b_param = 5
    recency_score = float(np.clip(np.random.beta(a=a_param, b=b_param), 0.0, 1.0))

    return {
        "avg_sentiment_score": float(np.mean(sentiments)),
        "avg_intent_score": float(np.mean(intents)),
        "avg_urgency_score": float(np.mean(urgencies)),
        "conversation_count": convo_count,
        "recency_score": recency_score,
    }


# ---------------------------------------------------------------------------
# Load base tables
# ---------------------------------------------------------------------------
crm = pd.read_csv(RAW_DATA_DIR / "crm_leads.csv")
activity = pd.read_csv(RAW_DATA_DIR / "activity_logs.csv")
marketing = pd.read_csv(RAW_DATA_DIR / "marketing_data.csv")

# Merge non-conversation sources first
data = crm.merge(activity, on="lead_id")
data = data.merge(marketing, on="lead_id")

# ---------------------------------------------------------------------------
# Construct latent conversion propensity (business heuristic + noise)
# ---------------------------------------------------------------------------
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

score = (score - score.min()) / (score.max() - score.min())
noise = np.random.normal(0, 0.08, len(score))
probability = np.clip(score + noise, 0, 1)

# ---------------------------------------------------------------------------
# Generate conversation aggregates conditioned on propensity
# ---------------------------------------------------------------------------
conversation_features = data[["lead_id"]].copy()
conversation_features = conversation_features.assign(**{
    "avg_sentiment_score": 0.0,
    "avg_intent_score": 0.0,
    "avg_urgency_score": 0.0,
    "conversation_count": 0,
    "recency_score": 1.0,
})

for idx, p in enumerate(probability):
    feats = _sample_conversation_features(p)
    conversation_features.iloc[idx, conversation_features.columns.get_loc("avg_sentiment_score")] = feats["avg_sentiment_score"]
    conversation_features.iloc[idx, conversation_features.columns.get_loc("avg_intent_score")] = feats["avg_intent_score"]
    conversation_features.iloc[idx, conversation_features.columns.get_loc("avg_urgency_score")] = feats["avg_urgency_score"]
    conversation_features.iloc[idx, conversation_features.columns.get_loc("conversation_count")] = feats["conversation_count"]
    conversation_features.iloc[idx, conversation_features.columns.get_loc("recency_score")] = feats["recency_score"]

# Optionally persist the synthesized conversation features for inspection/reuse
conversation_features.to_csv(RAW_DATA_DIR / "conversation_features.csv", index=False)

# Merge conversation features back into the dataset
data = data.merge(conversation_features, on="lead_id", how="left")

# ---------------------------------------------------------------------------
# Create target using propensity threshold
# ---------------------------------------------------------------------------
threshold = np.percentile(probability, 70)
data["converted"] = (probability > threshold).astype(int)

data.to_csv(PROCESSED_DATA_DIR / "consolidated_leads.csv", index=False)

print("Data consolidated and target created.")
print("Conversion Rate:", data["converted"].mean())