"""Data preprocessing utilities for the AQI prediction project."""

from __future__ import annotations

import os
from typing import Tuple

import joblib

os.environ.setdefault("MPLCONFIGDIR", os.path.join(os.getcwd(), ".matplotlib"))

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


FEATURE_COLUMNS = ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]
TARGET_COLUMN = "AQI"


def load_data(filepath: str) -> pd.DataFrame:
    """Load the AQI dataset from disk and support zipped CSV input when needed."""
    try:
        compression = "zip" if filepath.lower().endswith(".csv") else "infer"
        return pd.read_csv(filepath, compression=compression)
    except Exception:
        try:
            return pd.read_csv(filepath)
        except Exception as exc:
            st.error(f"Unable to load dataset from {filepath}: {exc}")
            return pd.DataFrame()


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows with missing AQI values and median-fill other numeric nulls."""
    try:
        cleaned_df = df.copy()
        cleaned_df = cleaned_df.dropna(subset=[TARGET_COLUMN])

        numeric_columns = cleaned_df.select_dtypes(include=["number"]).columns
        for column in numeric_columns:
            if cleaned_df[column].isna().any():
                cleaned_df[column] = cleaned_df[column].fillna(
                    cleaned_df[column].median()
                )

        return cleaned_df
    except Exception as exc:
        st.error(f"Unable to clean dataset: {exc}")
        return df


def remove_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """Remove AQI outliers using the interquartile range method."""
    try:
        q1 = df[TARGET_COLUMN].quantile(0.25)
        q3 = df[TARGET_COLUMN].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        return df[
            (df[TARGET_COLUMN] >= lower_bound) & (df[TARGET_COLUMN] <= upper_bound)
        ].copy()
    except Exception as exc:
        st.error(f"Unable to remove AQI outliers: {exc}")
        return df


def get_features_and_target(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Return the model feature matrix and target vector."""
    try:
        return df[FEATURE_COLUMNS].copy(), df[TARGET_COLUMN].copy()
    except Exception as exc:
        st.error(f"Unable to extract features and target: {exc}")
        return pd.DataFrame(columns=FEATURE_COLUMNS), pd.Series(dtype="float64")


def scale_features(
    X_train: pd.DataFrame, X_test: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame, StandardScaler]:
    """Scale train and test features and persist the fitted scaler to disk."""
    try:
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        models_dir = os.path.join(os.getcwd(), "models")
        os.makedirs(models_dir, exist_ok=True)
        scaler_path = os.path.join(models_dir, "scaler.pkl")
        joblib.dump(scaler, scaler_path)

        return X_train_scaled, X_test_scaled, scaler
    except Exception as exc:
        st.error(f"Unable to scale and save features: {exc}")
        return X_train, X_test, StandardScaler()


def split_data(
    X: pd.DataFrame, y: pd.Series, test_size: float = 0.2, random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Split features and target into train and test partitions."""
    try:
        return train_test_split(X, y, test_size=test_size, random_state=random_state)
    except Exception as exc:
        st.error(f"Unable to split dataset: {exc}")
        empty_features = pd.DataFrame(
            columns=X.columns if not X.empty else FEATURE_COLUMNS
        )
        empty_target = pd.Series(dtype="float64")
        return empty_features, empty_features, empty_target, empty_target


def create_correlation_heatmap(df: pd.DataFrame) -> plt.Figure:
    """Create a correlation heatmap for the AQI feature set."""
    try:
        chart_df = df[FEATURE_COLUMNS + [TARGET_COLUMN]].copy()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(chart_df.corr(), annot=True, cmap="YlGnBu", fmt=".2f", ax=ax)
        ax.set_title("Feature Correlation Heatmap")
        fig.tight_layout()
        return fig
    except Exception as exc:
        st.error(f"Unable to create correlation heatmap: {exc}")
        return plt.figure()


def create_aqi_distribution_chart(df: pd.DataFrame) -> plt.Figure:
    """Create a histogram showing the AQI target distribution."""
    try:
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.histplot(df[TARGET_COLUMN], bins=30, kde=True, color="#2c7fb8", ax=ax)
        ax.set_title("AQI Distribution")
        ax.set_xlabel("AQI")
        ax.set_ylabel("Frequency")
        fig.tight_layout()
        return fig
    except Exception as exc:
        st.error(f"Unable to create AQI distribution chart: {exc}")
        return plt.figure()


def create_city_trend_chart(df: pd.DataFrame, city: str) -> plt.Figure:
    """Create a city-wise AQI trend line chart for the selected city."""
    try:
        city_df = df[df["City"] == city].copy()
        city_df["Date"] = pd.to_datetime(city_df["Date"], errors="coerce")
        city_df = city_df.dropna(subset=["Date"]).sort_values("Date")

        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(city_df["Date"], city_df[TARGET_COLUMN], color="#1d3557", linewidth=2)
        ax.set_title(f"AQI Trend for {city}")
        ax.set_xlabel("Date")
        ax.set_ylabel("AQI")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        return fig
    except Exception as exc:
        st.error(f"Unable to create city trend chart: {exc}")
        return plt.figure()
