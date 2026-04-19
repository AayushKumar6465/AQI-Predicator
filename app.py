"""Streamlit web application for AQI prediction."""

from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from src.data_preprocessing import (
    clean_data,
    create_aqi_distribution_chart,
    create_city_trend_chart,
    create_correlation_heatmap,
    get_features_and_target,
    load_data,
    remove_outliers,
    scale_features,
    split_data,
)
from src.model_training import train_all_models
from src.prediction import (
    create_feature_importance_chart,
    export_prediction_csv,
    get_aqi_category,
    load_model,
    load_model_results,
    predict_aqi,
)


st.set_page_config(page_title="AQI Predictor", layout="wide")


@st.cache_data
def get_processed_data() -> pd.DataFrame:
    """Load and preprocess the source dataset for model training and visualization."""
    dataset_path = os.path.join(os.getcwd(), "data", "aqi_data.csv")
    df = load_data(dataset_path)
    if df.empty:
        return df
    df = clean_data(df)
    df = remove_outliers(df)
    return df


@st.cache_resource
def get_or_train_artifacts():
    """Load model artifacts if present, otherwise train and save them."""
    models_dir = os.path.join(os.getcwd(), "models")
    model_path = os.path.join(models_dir, "trained_model.pkl")
    scaler_path = os.path.join(models_dir, "scaler.pkl")
    results_path = os.path.join(models_dir, "model_results.json")
    rf_model_path = os.path.join(models_dir, "random_forest_model.pkl")

    if all(
        os.path.exists(path)
        for path in [model_path, scaler_path, results_path, rf_model_path]
    ):
        model, scaler = load_model()
        results = load_model_results()
        return model, scaler, results

    df = get_processed_data()
    if df.empty:
        return None, None, {}

    X, y = get_features_and_target(df)
    X_train, X_test, y_train, y_test = split_data(X, y)
    X_train_scaled, X_test_scaled, scaler = scale_features(X_train, X_test)
    best_model, results = train_all_models(
        X_train_scaled, X_test_scaled, y_train, y_test
    )
    return best_model, scaler, results


def build_metrics_table(results_payload: dict) -> pd.DataFrame:
    """Transform saved model metrics into a display-friendly dataframe."""
    results = results_payload.get("results", {})
    metrics_df = pd.DataFrame(
        [
            {"Model": name, "R²": metrics["r2"], "RMSE": metrics["rmse"]}
            for name, metrics in results.items()
        ]
    )
    if metrics_df.empty:
        return metrics_df
    return metrics_df.sort_values("RMSE", ascending=True).reset_index(drop=True)


def highlight_best_model(row: pd.Series, best_model_name: str):
    """Apply styling to the best-performing model row."""
    style = (
        "background-color: #d9f2d9; font-weight: 600;"
        if row["Model"] == best_model_name
        else ""
    )
    return [style] * len(row)


def main() -> None:
    """Render the Streamlit AQI Predictor interface."""
    st.title("AQI Prediction Web App")
    st.caption(
        "Predict AQI from key air-pollution indicators and inspect model behavior."
    )

    with st.sidebar:
        st.header("Input Pollutant Levels")
        input_data = {
            "PM2.5": st.slider(
                "PM2.5", min_value=0.0, max_value=500.0, value=80.0, step=1.0
            ),
            "PM10": st.slider(
                "PM10", min_value=0.0, max_value=600.0, value=120.0, step=1.0
            ),
            "NO2": st.slider(
                "NO2", min_value=0.0, max_value=200.0, value=40.0, step=1.0
            ),
            "SO2": st.slider(
                "SO2", min_value=0.0, max_value=100.0, value=15.0, step=1.0
            ),
            "CO": st.slider("CO", min_value=0.0, max_value=50.0, value=2.0, step=0.1),
            "O3": st.slider("O3", min_value=0.0, max_value=300.0, value=30.0, step=1.0),
        }

    df = get_processed_data()
    model, scaler, results_payload = get_or_train_artifacts()

    if df.empty or model is None or scaler is None:
        st.error(
            "App setup is incomplete because the dataset or model artifacts could not be prepared."
        )
        return

    predicted_aqi = predict_aqi(model, scaler, input_data)
    category = get_aqi_category(predicted_aqi)

    st.subheader("Prediction Result")
    metric_col, category_col, advice_col = st.columns(3)

    with metric_col:
        st.markdown(
            f"""
            <div style="padding: 1rem; border-radius: 14px; background: #f5f7fb; text-align: center;">
                <div style="font-size: 0.95rem; color: #5b6573;">Predicted AQI</div>
                <div style="font-size: 2.8rem; font-weight: 700; color: #1d3557;">{predicted_aqi:.2f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with category_col:
        st.markdown(
            f"""
            <div style="padding: 1rem; border-radius: 14px; background: {category["color_hex"]}; text-align: center;">
                <div style="font-size: 0.95rem; color: #111111;">Category</div>
                <div style="font-size: 2rem; font-weight: 700; color: #111111;">{category["category"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with advice_col:
        st.markdown(
            f"""
            <div style="padding: 1rem; border-radius: 14px; background: #fff8e8; height: 100%;">
                <div style="font-size: 0.95rem; color: #8a6d3b;">Health Advice</div>
                <div style="font-size: 1.1rem; font-weight: 500; color: #5b4636;">{category["advice"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    csv_output = export_prediction_csv(input_data, predicted_aqi, category)
    st.download_button(
        label="Download Prediction as CSV",
        data=csv_output,
        file_name="aqi_prediction.csv",
        mime="text/csv",
    )

    st.subheader("Model Performance")
    metrics_df = build_metrics_table(results_payload)
    best_model_name = results_payload.get("best_model", "")
    if metrics_df.empty:
        st.warning("Model performance results are not available.")
    else:
        styled_table = metrics_df.style.format(
            {"R²": "{:.4f}", "RMSE": "{:.4f}"}
        ).apply(highlight_best_model, best_model_name=best_model_name, axis=1)
        st.dataframe(styled_table, use_container_width=True)

    st.subheader("Visualizations")
    heatmap_tab, importance_tab, distribution_tab, trend_tab = st.tabs(
        [
            "Correlation Heatmap",
            "Feature Importance",
            "AQI Distribution",
            "City-wise AQI Trend",
        ]
    )

    with heatmap_tab:
        st.pyplot(create_correlation_heatmap(df), use_container_width=True)

    with importance_tab:
        st.pyplot(create_feature_importance_chart(), use_container_width=True)

    with distribution_tab:
        st.pyplot(create_aqi_distribution_chart(df), use_container_width=True)

    with trend_tab:
        city_options = sorted(df["City"].dropna().unique().tolist())
        selected_city = st.selectbox("Select City", city_options)
        st.pyplot(create_city_trend_chart(df, selected_city), use_container_width=True)


if __name__ == "__main__":
    main()
