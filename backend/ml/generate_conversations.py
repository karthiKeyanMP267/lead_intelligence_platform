"""Generate a synthetic conversation feature dataset for leads.

Outputs: data/raw/conversation_features.csv
Columns: lead_id, avg_sentiment_score, avg_intent_score, avg_urgency_score, conversation_count, recency_score

This avoids calling transformers during data synthesis; we approximate intent/urgency/sentiment with templates.
"""
import random
from pathlib import Path
import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

N_LEADS = 20000

templates = [
    {
        "label": "high purchase intent",
        "urgency_label": "pricing inquiry",
        "text": "We are ready to move forward. Can you share the pricing and contract to start this month?",
        "sentiment": 0.82,
        "intent": 0.9,
        "urgency": 0.9,
    },
    {
        "label": "pricing inquiry",
        "urgency_label": "pricing inquiry",
        "text": "Need a detailed quote and any volume discounts you offer.",
        "sentiment": 0.55,
        "intent": 0.7,
        "urgency": 0.85,
    },
    {
        "label": "technical discussion",
        "urgency_label": "technical discussion",
        "text": "We must confirm the API limits and SSO support before proceeding.",
        "sentiment": 0.42,
        "intent": 0.55,
        "urgency": 0.5,
    },
    {
        "label": "objection",
        "urgency_label": "technical discussion",
        "text": "Security review raised concerns about data residency and audit logs.",
        "sentiment": -0.35,
        "intent": 0.25,
        "urgency": 0.45,
    },
    {
        "label": "low engagement",
        "urgency_label": "low engagement",
        "text": "Just checking what this is about. Not sure we need it right now.",
        "sentiment": 0.05,
        "intent": 0.1,
        "urgency": 0.1,
    },
    {
        "label": "low engagement",
        "urgency_label": "low engagement",
        "text": "Please remove me from further emails.",
        "sentiment": -0.6,
        "intent": 0.05,
        "urgency": 0.05,
    },
]


def sample_conversations(count: int):
    rows = []
    for _ in range(count):
        t = random.choice(templates)
        # Add mild noise so aggregates differ per conversation
        sentiment = float(np.clip(np.random.normal(t["sentiment"], 0.08), -1.0, 1.0))
        intent = float(np.clip(np.random.normal(t["intent"], 0.05), 0.0, 1.0))
        urgency = float(np.clip(np.random.normal(t["urgency"], 0.07), 0.0, 1.0))
        rows.append((sentiment, intent, urgency))
    return rows


def main():
    lead_ids = range(1, N_LEADS + 1)
    convo_records = []

    for lead_id in lead_ids:
        # Most leads have 0-3 conversations, with a long tail up to 6
        convo_count = int(np.clip(np.random.poisson(lam=1.2), 0, 6))
        if convo_count == 0:
            convo_records.append(
                {
                    "lead_id": lead_id,
                    "avg_sentiment_score": 0.0,
                    "avg_intent_score": 0.0,
                    "avg_urgency_score": 0.0,
                    "conversation_count": 0,
                    # Older/no conversations → recency closer to 1
                    "recency_score": 1.0,
                }
            )
            continue

        convos = sample_conversations(convo_count)
        sentiments, intents, urgencies = zip(*convos)
        recency_score = float(np.clip(np.random.beta(a=2, b=5), 0.0, 1.0))

        convo_records.append(
            {
                "lead_id": lead_id,
                "avg_sentiment_score": float(np.mean(sentiments)),
                "avg_intent_score": float(np.mean(intents)),
                "avg_urgency_score": float(np.mean(urgencies)),
                "conversation_count": convo_count,
                # Recent conversations → smaller recency_score
                "recency_score": recency_score,
            }
        )

    df = pd.DataFrame(convo_records)
    df.to_csv(RAW_DATA_DIR / "conversation_features.csv", index=False)
    print(f"conversation_features.csv written with {len(df)} rows")


if __name__ == "__main__":
    main()
