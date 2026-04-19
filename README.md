# AQI Predictor

AQI Predictor is a Streamlit web app that trains multiple regression models on air-quality data and predicts AQI from pollutant inputs such as PM2.5, PM10, NO2, SO2, CO, and O3.

## Project Structure

```text
AQI_Predictor/
├── data/
│   └── aqi_data.csv
├── models/
│   ├── scaler.pkl
│   ├── trained_model.pkl
│   └── model_results.json
├── src/
│   ├── data_preprocessing.py
│   ├── model_training.py
│   └── prediction.py
├── app.py
├── requirements.txt
└── README.md
```

## Features

- Cleans the dataset by dropping missing target rows and filling other numeric nulls with medians
- Removes AQI outliers using the IQR rule
- Trains `LinearRegression`, `RandomForestRegressor`, and `XGBRegressor`
- Saves the best-performing model, scaler, and metrics under `models/`
- Predicts AQI from sidebar inputs
- Shows AQI category, health advice, model comparison, and visual analytics
- Supports CSV download for prediction results

## Setup

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## Notes

- The provided dataset file is handled even when it is a zipped CSV archive with a `.csv` extension.
- Model artifacts are created automatically the first time the app runs.
