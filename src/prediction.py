import json
import pickle
from io import StringIO
import joblib
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

from src.data_preprocessing import FEATURE_COLUMNS

MODELS_DIR = "models"


# LOAD MODEL
def load_model():
    try:
        model = pickle.load(open(f"{MODELS_DIR}/trained_model.pkl", "rb"))
        scaler = joblib.load(f"{MODELS_DIR}/scaler.pkl")
        return model, scaler
    except Exception as e:
        st.error(f"Model load error: {e}")
        return None, None


# PREDICTION
def predict_aqi(model, scaler, inputs):
    df = pd.DataFrame([inputs])
    scaled = scaler.transform(df)
    return float(model.predict(scaled)[0])


# AQI CATEGORY
def get_aqi_category(aqi):
    if aqi <= 50:
        return {"category": "Good", "color": "#00e400"}
    elif aqi <= 100:
        return {"category": "Satisfactory", "color": "#92d050"}
    elif aqi <= 200:
        return {"category": "Moderate", "color": "#ffff00"}
    elif aqi <= 300:
        return {"category": "Poor", "color": "#ff7e00"}
    elif aqi <= 400:
        return {"category": "Very Poor", "color": "#ff0000"}
    else:
        return {"category": "Severe", "color": "#7e0023"}


# LOAD RESULTS
def load_model_results():
    try:
        return json.load(open(f"{MODELS_DIR}/model_results.json"))
    except Exception as e:
        st.error(f"Error loading results: {e}")
        return {}


# FEATURE IMPORTANCE
def feature_importance_plot():
    fig, ax = plt.subplots()

    try:
        model = pickle.load(open(f"{MODELS_DIR}/random_forest_model.pkl", "rb"))

        df = pd.DataFrame(
            {"Feature": FEATURE_COLUMNS, "Importance": model.feature_importances_}
        ).sort_values("Importance", ascending=False)

        sns.barplot(data=df, x="Importance", y="Feature", ax=ax)

    except Exception:
        sns.barplot(x=[0] * len(FEATURE_COLUMNS), y=FEATURE_COLUMNS, ax=ax)

    ax.set_title("Feature Importance")
    return fig


# EXPORT CSV
def export_csv(inputs, aqi, category):
    data = {**inputs, "Predicted_AQI": aqi, "Category": category}
    buffer = StringIO()
    pd.DataFrame([data]).to_csv(buffer, index=False)
    return buffer.getvalue()
