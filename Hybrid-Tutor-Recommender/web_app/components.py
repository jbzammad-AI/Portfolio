import streamlit as st

def display_ranked_table(df):
    st.dataframe(df)

def display_shap_explanation(shap_values):
    st.pyplot(shap.plots.beeswarm(shap_values))
