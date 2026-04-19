"""Model training utilities for the AQI prediction project."""

from __future__ import annotations

import json
import os
import pickle
from typing import Dict, Tuple

import numpy as np
import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from xgboost import XGBRegressor

from src.data_preprocessing import FEATURE_COLUMNS


def train_all_models(
    X_train, X_test, y_train, y_test
) -> Tuple[object, Dict[str, Dict[str, float]]]:
    """Train all supported regressors, evaluate them, and save the best model plus metrics."""
    try:
        models = {
            "Linear Regression": LinearRegression(),
            "Random Forest": RandomForestRegressor(
                n_estimators=300, max_depth=14, random_state=42, n_jobs=1
            ),
            "XGBoost": XGBRegressor(
                n_estimators=400,
                max_depth=6,
                learning_rate=0.05,
                subsample=0.9,
                colsample_bytree=0.9,
                objective="reg:squarederror",
                random_state=42,
                n_jobs=1,
            ),
        }

        results = {}
        trained_models = {}

        for model_name, model in models.items():
            if model_name == "Linear Regression":
                fitted_model = model.fit(X_train, y_train)
                predictions = fitted_model.predict(X_test)
            else:
                fitted_model = model.fit(y=y_train, X=X_train)
                predictions = fitted_model.predict(X_test)

            rmse = float(np.sqrt(mean_squared_error(y_test, predictions)))
            r2 = r2_score(y_test, predictions)
            results[model_name] = {"r2": float(r2), "rmse": rmse}
            trained_models[model_name] = fitted_model

        best_model_name = min(results, key=lambda name: results[name]["rmse"])
        best_model = trained_models[best_model_name]

        models_dir = os.path.join(os.getcwd(), "models")
        os.makedirs(models_dir, exist_ok=True)
        save_model(best_model, os.path.join(models_dir, "trained_model.pkl"))
        save_model(
            trained_models["Random Forest"],
            os.path.join(models_dir, "random_forest_model.pkl"),
        )

        results_payload = {
            "best_model": best_model_name,
            "feature_columns": FEATURE_COLUMNS,
            "results": results,
        }
        results_path = os.path.join(models_dir, "model_results.json")
        with open(results_path, "w", encoding="utf-8") as file:
            json.dump(results_payload, file, indent=4)

        return best_model, results_payload
    except Exception as exc:
        st.error(f"Unable to train models: {exc}")
        return None, {}


def save_model(model: object, filepath: str) -> None:
    """Persist a trained model to disk."""
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "wb") as file:
            pickle.dump(model, file)
    except Exception as exc:
        st.error(f"Unable to save model to {filepath}: {exc}")
