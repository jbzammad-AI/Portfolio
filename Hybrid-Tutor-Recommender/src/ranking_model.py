import xgboost as xgb
import numpy as np
import shap
import os

# -----------------------------
# Train XGBoost model
# -----------------------------
def train_model(X, y, save_path="models/xgb_model.json"):
    """
    Train XGBoost classifier on numeric + tutor embeddings only.
    """
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        use_label_encoder=False,
        eval_metric='logloss'
    )
    model.fit(X, y)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    model.save_model(save_path)
    return model

# -----------------------------
# Load saved model
# -----------------------------
def load_model(path="models/xgb_model.json"):
    model = xgb.XGBClassifier()
    model.load_model(path)
    return model

# -----------------------------
# SHAP explanations
# -----------------------------
def explain_predictions_human(model, X, feature_names):
    """
    Returns human-readable explanations for each prediction.
    """
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)
        explanations = []

        for row_idx in range(X.shape[0]):
            impact = {}
            for f_idx, f_name in enumerate(feature_names):
                val = X[row_idx, f_idx]
                shap_val = shap_values[row_idx][f_idx]
                if abs(shap_val) > 0.01:
                    impact[f_name] = shap_val
            impact_str = ", ".join([f"{k} {'high' if v>0 else 'low'}" for k,v in impact.items()])
            explanations.append(impact_str if impact_str else "No major feature impact")

        return explanations
    except Exception:
        return ["No SHAP explanation"] * X.shape[0]
