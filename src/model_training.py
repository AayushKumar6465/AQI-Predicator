import os
import json
import pickle
import numpy as np
import streamlit as st

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
from xgboost import XGBRegressor

from src.data_preprocessing import FEATURE_COLUMNS

MODELS_DIR = "models"

# MODELS
MODELS = {
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(n_estimators=300, max_depth=14),
    "XGBoost": XGBRegressor(n_estimators=400, max_depth=6),
}


# SAVE MODEL
def save_model(model, path):
    os.makedirs("models", exist_ok=True)
    pickle.dump(model, open(path, "wb"))


# TRAIN
def train_models(X_train, X_test, y_train, y_test):
    results = {}
    trained = {}

    try:
        for name, model in MODELS.items():
            model.fit(X_train, y_train)
            pred = model.predict(X_test)

            results[name] = {
                "r2": float(r2_score(y_test, pred)),
                "rmse": float(np.sqrt(mean_squared_error(y_test, pred))),
            }

            trained[name] = model

        # best model (lowest RMSE)
        best_model_name = min(results, key=lambda x: results[x]["rmse"])

        save_model(trained[best_model_name], f"{MODELS_DIR}/trained_model.pkl")
        save_model(trained["Random Forest"], f"{MODELS_DIR}/random_forest_model.pkl")

        data = {
            "best_model": best_model_name,
            "results": results,
            "features": FEATURE_COLUMNS,
        }

        json.dump(data, open(f"{MODELS_DIR}/model_results.json", "w"), indent=4)

        return trained[best_model_name], data

    except Exception as e:
        st.error(f"Training error: {e}")
        return None, {}
