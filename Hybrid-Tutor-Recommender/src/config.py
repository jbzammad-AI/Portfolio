import os

# Paths
RAW_DATA_PATH = "data/raw/"
PROCESSED_DATA_PATH = "data/processed/"
EMBEDDINGS_PATH = "data/embeddings/"
MODEL_PATH = "models/xgb_model.json"
SCALER_PATH = "models/scaler.pkl"
PCA_PATH = "models/pca.pkl"

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Hyperparameters
EMBED_DIM = 128
XGB_PARAMS = {
    "n_estimators": 500,
    "max_depth": 6,
    "learning_rate": 0.05,
    "objective": "binary:logistic",
    "random_state": 42
}
