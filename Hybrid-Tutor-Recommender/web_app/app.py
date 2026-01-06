import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

from src.data_pipeline import load_data, merge_datasets, preprocess
from src.ranking_model import load_model, train_model, explain_predictions_human

# OpenAI embeddings (optional)
try:
    from src.embeddings import get_embedding, reduce_embeddings
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="Hybrid Tutor Recommender", layout="wide")
st.title("Hybrid Tutor Recommendation System")

# -----------------------------
# Load processed data
# -----------------------------
@st.cache_data
def load_processed_data():
    processed_path = "data/processed/merged_data.csv"
    if os.path.exists(processed_path):
        df = pd.read_csv(processed_path)
    else:
        cases, tutors, results = load_data()
        df = merge_datasets(cases, tutors, results)
        df = preprocess(df)
        os.makedirs("data/processed", exist_ok=True)
        df.to_csv(processed_path, index=False)
    return df

df = load_processed_data()

# -----------------------------
# Load embeddings safely
# -----------------------------
@st.cache_data
def load_embeddings(df):
    emb_path = "data/embeddings/embeddings_reduced.npy"
    os.makedirs("data/embeddings", exist_ok=True)

    if os.path.exists(emb_path):
        embeddings = np.load(emb_path)
        st.info("✅ Loaded embeddings")
    else:
        n_rows = len(df)
        n_features = 32
        embeddings = None
        if OPENAI_AVAILABLE:
            try:
                texts = list(df['tutor_bio'])
                raw_emb = [get_embedding(t) for t in texts]
                embeddings = reduce_embeddings(np.array(raw_emb))
                st.info("✅ OpenAI embeddings generated")
            except:
                st.warning("⚠ OpenAI failed, using dummy embeddings")
        if embeddings is None:
            embeddings = np.random.rand(n_rows, n_features)
            st.info("✅ Using dummy embeddings")
        np.save(emb_path, embeddings)
    return embeddings

embeddings = load_embeddings(df)

# -----------------------------
# Encode numeric/categorical
# -----------------------------
def encode_features(df):
    df_enc = df.copy()
    cat_cols = ['preferred_gender','gender']
    for col in cat_cols:
        if col in df_enc.columns:
            df_enc[col] = df_enc[col].astype('category').cat.codes
    # drop text columns to avoid XGBoost errors
    text_cols = ['case_description','case_description_input','tutor_name','tutor_bio']
    for col in text_cols:
        if col in df_enc.columns:
            df_enc = df_enc.drop(columns=[col])
    return df_enc

df_enc = encode_features(df)

# -----------------------------
# Combine numeric + tutor embeddings only
# -----------------------------
def combine_features(df_enc, embeddings):
    X_numeric = df_enc.drop(columns=['success','case_id','tutor_id'], errors='ignore').values
    if embeddings.shape[0] != df_enc.shape[0]:
        emb_numeric = embeddings[-df_enc.shape[0]:]
    else:
        emb_numeric = embeddings
    X_combined = np.hstack([X_numeric, emb_numeric])
    X_scaled = StandardScaler().fit_transform(X_combined)
    return X_scaled

X = combine_features(df_enc, embeddings)
y = df_enc['success'].values

# -----------------------------
# Load/train model
# -----------------------------
@st.cache_resource
def get_model(X, y):
    model_path = "models/xgb_model.json"
    os.makedirs("models", exist_ok=True)
    if os.path.exists(model_path):
        model = load_model(model_path)
        st.info("✅ Loaded trained model")
    else:
        model = train_model(X, y, save_path=model_path)
        st.info("✅ Model trained and saved")
    return model

model = get_model(X, y)

# -----------------------------
# Sidebar: New Case
# -----------------------------
st.sidebar.header("New Case Input")
case_desc = st.sidebar.text_area("Case Description", "A-Level Physics student, SEN-friendly")
budget = st.sidebar.slider("Budget (HKD/hour)", 30, 200, 100)

# -----------------------------
# Rank tutors
# -----------------------------
def rank_tutors(df, model, embeddings, case_desc, budget):
    df_temp = df.copy()
    df_temp['case_budget'] = budget
    df_numeric = encode_features(df_temp)
    X_numeric = df_numeric.drop(columns=['success','case_id','tutor_id'], errors='ignore').values

    # ✅ Combine numeric + tutor embeddings ONLY (match training features)
    X_combined = np.hstack([X_numeric, embeddings[-df_numeric.shape[0]:]])
    X_scaled = StandardScaler().fit_transform(X_combined)

    df_temp['ai_score'] = model.predict_proba(X_scaled)[:,1]

    feature_cols = df_numeric.drop(columns=['success','case_id','tutor_id'], errors='ignore').columns.tolist()
    df_temp['reason'] = explain_predictions_human(model, X_scaled, feature_cols)

    df_top = df_temp.sort_values(by='ai_score', ascending=False).head(10)
    return df_top[['tutor_name','tutor_rate','ai_score','reason']]

# -----------------------------
# Show top tutors
# -----------------------------
st.subheader("Top Tutor Recommendations")
top_tutors = rank_tutors(df, model, embeddings, case_desc, budget)
st.dataframe(top_tutors)

# -----------------------------
# Dynamic Pricing Simulator
# -----------------------------
st.subheader("Dynamic Pricing Simulator")
budgets = list(range(max(10, budget-20), budget+41, 10))
pricing_df = pd.DataFrame({
    'budget': budgets,
    'probability': [np.mean(top_tutors['ai_score']) for b in budgets]
})
st.line_chart(pricing_df.rename(columns={'budget':'index','probability':'value'}).set_index('index'))
