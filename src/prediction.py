"""Prediction and visualization helpers for the AQI prediction project."""

from __future__ import annotations

import json
import os
import pickle
from io import StringIO
from typing import Dict, Tuple

import joblib

os.environ.setdefault("MPLCONFIGDIR", os.path.join(os.getcwd(), ".matplotlib"))

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from src.data_preprocessing import FEATURE_COLUMNS


def load_model() -> Tuple[object, object]:
    """Load the trained model and scaler from disk."""
    try:
        models_dir = os.path.join(os.getcwd(), "models")
        model_path = os.path.join(models_dir, "trained_model.pkl")
        scaler_path = os.path.join(models_dir, "scaler.pkl")

        with open(model_path, "rb") as model_file:
            model = pickle.load(model_file)
        scaler = joblib.load(scaler_path)

        return model, scaler
    except Exception as exc:
        st.error(f"Unable to load model artifacts: {exc}")
        return None, None


def predict_aqi(model: object, scaler: object, input_dict: Dict[str, float]) -> float:
    """Generate an AQI prediction from user-provided pollutant values."""
    try:
        input_df = pd.DataFrame([input_dict], columns=FEATURE_COLUMNS)
        scaled_input = scaler.transform(input_df)
        prediction = model.predict(scaled_input)[0]
        return float(prediction)
    except Exception as exc:
        st.error(f"Unable to generate prediction: {exc}")
        return 0.0


def get_aqi_category(aqi_value: float) -> Dict[str, str]:
    """Map an AQI value to its category, display color, and health advice."""
    if aqi_value <= 50:
        return {
            "category": "Good",
            "color_hex": "#00e400",
            "advice": "Air quality is satisfactory.",
        }
    if aqi_value <= 100:
        return {
            "category": "Satisfactory",
            "color_hex": "#92d050",
            "advice": "Acceptable for most people.",
        }
    if aqi_value <= 200:
        return {
            "category": "Moderate",
            "color_hex": "#ffff00",
            "advice": "Sensitive groups may be affected.",
        }
    if aqi_value <= 300:
        return {
            "category": "Poor",
            "color_hex": "#ff7e00",
            "advice": "Everyone may experience effects.",
        }
    if aqi_value <= 400:
        return {
            "category": "Very Poor",
            "color_hex": "#ff0000",
            "advice": "Health alert for everyone.",
        }
    return {
        "category": "Severe",
        "color_hex": "#7e0023",
        "advice": "Emergency conditions.",
    }


def load_model_results() -> Dict[str, object]:
    """Load model comparison metrics from disk."""
    try:
        results_path = os.path.join(os.getcwd(), "models", "model_results.json")
        with open(results_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as exc:
        st.error(f"Unable to load model results: {exc}")
        return {}


def create_feature_importance_chart() -> plt.Figure:
    """Create a feature importance bar chart using the saved Random Forest model."""
    try:
        model_path = os.path.join(os.getcwd(), "models", "random_forest_model.pkl")
        with open(model_path, "rb") as file:
            model = pickle.load(file)

        if not hasattr(model, "feature_importances_"):
            raise AttributeError(
                "Saved Random Forest model does not expose feature importances."
            )

        importance_df = pd.DataFrame(
            {"Feature": FEATURE_COLUMNS, "Importance": model.feature_importances_}
        ).sort_values("Importance", ascending=False)

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(
            data=importance_df, x="Importance", y="Feature", palette="Greens_r", ax=ax
        )
        ax.set_title("Feature Importance")
        fig.tight_layout()
        return fig
    except Exception as exc:
        st.error(
            f"Unable to create feature importance chart from the Random Forest model: {exc}"
        )
        fig, ax = plt.subplots(figsize=(10, 5))
        empty_df = pd.DataFrame(
            {"Feature": FEATURE_COLUMNS, "Importance": [0.0] * len(FEATURE_COLUMNS)}
        )
        sns.barplot(data=empty_df, x="Importance", y="Feature", color="#74c476", ax=ax)
        ax.set_title("Feature Importance")
        fig.tight_layout()
        return fig


def export_prediction_csv(
    input_dict: Dict[str, float], predicted_aqi: float, category: Dict[str, str]
) -> str:
    """Build a CSV string for the current prediction result."""
    try:
        payload = {
            **input_dict,
            "Predicted_AQI": round(predicted_aqi, 2),
            "Category": category["category"],
        }
        buffer = StringIO()
        pd.DataFrame([payload]).to_csv(buffer, index=False)
        return buffer.getvalue()
    except Exception as exc:
        st.error(f"Unable to export prediction CSV: {exc}")
        return ""
