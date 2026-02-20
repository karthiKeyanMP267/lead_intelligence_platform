import pandas as pd
import joblib
import json
import os
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "consolidated_leads.csv"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Load processed dataset
data = pd.read_csv(PROCESSED_DATA_PATH)

# Split features and target
X = data.drop(["converted", "lead_id"], axis=1)
y = data["converted"]

# One-hot encode categorical features
X = pd.get_dummies(X, drop_first=True)

# Train-test split (stratified to maintain class balance)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# -------------------------------
# Define candidate models
# -------------------------------
models = {
    "LogisticRegression": Pipeline([
        ("scaler", StandardScaler()),
        ("lr", LogisticRegression(max_iter=2000))
    ]),
    "XGBoost": XGBClassifier(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    ),
    "LightGBM": LGBMClassifier(
        n_estimators=300,
        learning_rate=0.05,
        num_leaves=31,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )
}

results = {}

# -------------------------------
# Train & Evaluate All Models
# -------------------------------
for name, model in models.items():
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    results[name] = {
        "precision": float(precision_score(y_test, y_pred)),
        "recall": float(recall_score(y_test, y_pred)),
        "f1": float(f1_score(y_test, y_pred)),
        "auc": float(roc_auc_score(y_test, y_prob))
    }

# -------------------------------
# Select Best Model by AUC
# -------------------------------
best_model_name = max(results, key=lambda x: results[x]["auc"])
best_model = models[best_model_name]

# Save best model
joblib.dump(best_model, MODELS_DIR / "best_model.pkl")

# Save selected model name
with open(MODELS_DIR / "model_name.txt", "w") as f:
    f.write(best_model_name)

# Save metrics comparison
with open(MODELS_DIR / "metrics.json", "w") as f:
    json.dump(results, f, indent=4)

# -------------------------------
# Extract Feature Importance
# -------------------------------
feature_importance = {}
feature_names = X.columns.tolist()

if hasattr(best_model, "feature_importances_"):
    importances = best_model.feature_importances_
    feature_importance = {
        feature: float(importance)
        for feature, importance in zip(feature_names, importances)
    }

elif best_model_name == "LogisticRegression":
    coef = best_model.named_steps["lr"].coef_[0]
    feature_importance = {
        feature: float(weight)
        for feature, weight in zip(feature_names, coef)
    }

if feature_importance:
    with open(MODELS_DIR / "feature_importance.json", "w") as f:
        json.dump(feature_importance, f, indent=4)
# -------------------------------
# Final Output
# -------------------------------
print("\nModel Comparison:")
print(json.dumps(results, indent=4))
print("\nBest model selected:", best_model_name)
print("Model and feature importance saved successfully.")