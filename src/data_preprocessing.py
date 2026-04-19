import os
import joblib
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


FEATURE_COLUMNS = ["PM2.5", "PM10", "NO2", "SO2", "CO", "O3"]
TARGET_COLUMN = "AQI"


# LOAD
def load_data(path):
    try:
        return pd.read_csv(path)
    except Exception as e:
        st.error(f"Load error: {e}")
        return pd.DataFrame()


# CLEAN
def clean_data(df):
    df = df.dropna(subset=[TARGET_COLUMN])

    for col in df.select_dtypes(include="number"):
        df[col].fillna(df[col].median(), inplace=True)

    return df


# REMOVE OUTLIERS
def remove_outliers(df):
    q1 = df[TARGET_COLUMN].quantile(0.25)
    q3 = df[TARGET_COLUMN].quantile(0.75)
    iqr = q3 - q1

    return df[
        (df[TARGET_COLUMN] >= q1 - 1.5 * iqr) & (df[TARGET_COLUMN] <= q3 + 1.5 * iqr)
    ]


# SPLIT
def split_data(X, y):
    return train_test_split(X, y, test_size=0.2, random_state=42)


# SCALE
def scale_data(X_train, X_test):
    scaler = StandardScaler()

    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    os.makedirs("models", exist_ok=True)
    joblib.dump(scaler, "models/scaler.pkl")

    return X_train, X_test, scaler


# VISUALS
def correlation_heatmap(df):
    fig, ax = plt.subplots()
    sns.heatmap(df.corr(), annot=True, ax=ax)
    return fig


def aqi_distribution(df):
    fig, ax = plt.subplots()
    sns.histplot(df[TARGET_COLUMN], bins=30, kde=True, ax=ax)
    return fig


def city_trend(df, city):
    df = df[df["City"] == city]
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")

    fig, ax = plt.subplots()
    ax.plot(df["Date"], df[TARGET_COLUMN])
    return fig
