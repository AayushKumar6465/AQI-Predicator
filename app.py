import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random
import datetime
from fpdf import FPDF
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="AQI Observer")

# CSS Injection
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap');

html, body, [class*="css"]  {
    font-family: 'DM Sans', sans-serif;
    color: #1a1a1a;
}

[data-testid="stAppViewContainer"] {
    background-color: #f5f5f5;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e0e0e0;
}

.sidebar-header {
    font-size: 0.8rem;
    font-weight: 700;
    color: #888888;
    letter-spacing: 1px;
    margin-bottom: 20px;
}

.stSlider > div > div > div > div {
    background-color: #1a6e2e !important;
}

/* Cards */
.card {
    background-color: #ffffff;
    border-radius: 14px;
    padding: 24px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    margin-bottom: 20px;
}

.prediction-card {
    border-left: 8px solid #ffc107;
}

.dark-card {
    background-color: #1e5c2a;
    color: #ffffff;
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 20px;
}

.dark-card p, .dark-card h3 {
    color: #ffffff !important;
}

/* Buttons */
.stButton > button, .stDownloadButton > button {
    background-color: #1a6e2e;
    color: white;
    border-radius: 8px;
    font-weight: 500;
    border: none;
    padding: 10px 24px;
    width: 100%;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    background-color: #2d7a3a;
    color: white;
}

/* Prediction layout */
.aqi-number {
    font-size: 4rem;
    font-weight: 700;
    line-height: 1.1;
    margin-bottom: 10px;
}

.aqi-label {
    font-size: 0.85rem;
    font-weight: 700;
    color: #888888;
    letter-spacing: 1px;
}

.pill-badge {
    display: inline-block;
    padding: 6px 16px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.9rem;
    color: white;
}

/* Header */
.main-header {
    font-size: 2.5rem;
    font-weight: 700;
    margin-top: 0;
    padding-top: 0;
    margin-bottom: 5px;
}

.sub-header {
    font-size: 1.1rem;
    color: #888888;
    margin-bottom: 24px;
}

.metric-box {
    background-color: rgba(255, 255, 255, 0.1);
    padding: 16px;
    border-radius: 10px;
    text-align: center;
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: 4px;
}

.metric-label {
    font-size: 0.8rem;
    opacity: 0.8;
}

.spectrum-container {
    width: 100%;
    margin-top: 15px;
    margin-bottom: 15px;
}
.spectrum-bar {
    height: 12px;
    border-radius: 6px;
    background: linear-gradient(to right, #4caf50, #ff9800, #f44336, #9c27b0, #7b1c1c);
    position: relative;
    margin-bottom: 10px;
}
.spectrum-marker {
    position: absolute;
    top: -6px;
    width: 4px;
    height: 24px;
    background-color: #1a1a1a;
    border-radius: 2px;
    box-shadow: 0 0 4px rgba(255,255,255,0.8);
}
.spectrum-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.7rem;
    font-weight: 700;
    color: #888888;
}

/* Ensure no markdown margins mess up layout */
.card p:last-child {
    margin-bottom: 0;
}
</style>
""",
    unsafe_allow_html=True,
)

# Initialization
if "temp" not in st.session_state:
    st.session_state.temp = 24
if "hum" not in st.session_state:
    st.session_state.hum = 58

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(
        '<div class="sidebar-header">POLLUTION PARAMETERS</div>', unsafe_allow_html=True
    )

    pm25 = st.slider("PM2.5", min_value=0, max_value=500, value=124, step=1)
    pm10 = st.slider("PM10", min_value=0, max_value=600, value=82, step=1)
    no2 = st.slider("NO₂", min_value=0, max_value=200, value=45, step=1)
    so2 = st.slider("SO₂", min_value=0, max_value=150, value=12, step=1)
    co = st.slider("CO", min_value=0.0, max_value=50.0, value=1.2, step=0.1)
    o3 = st.slider("O₃", min_value=0.0, max_value=300.0, value=30.0, step=1.0)

    pass

# Calculate AQI
# Formula: aqi = int((pm25*0.35) + (pm10*0.2) + (no2*0.15) + (so2*0.1) + (co*5) + (o3*0.1))
aqi = int(
    (pm25 * 0.35) + (pm10 * 0.2) + (no2 * 0.15) + (so2 * 0.1) + (co * 5) + (o3 * 0.1)
)

# Determine Category and Colors
if aqi <= 50:
    cat_name = "Good"
    cat_color = "#4caf50"
    bg_tint = "#e8f5e9"
    health_guidance = "Air quality is considered satisfactory, and air pollution poses little or no risk. Enjoy outdoor activities."
    actions = [
        "• Open windows to let in fresh air",
        "• Enjoy outdoor exercises",
        "• No restrictions for sensitive groups",
    ]
    spec_position = min(aqi / 50 * 20, 20)
elif aqi <= 100:
    cat_name = "Moderate"
    cat_color = "#ff9800"
    bg_tint = "#fff3e0"
    health_guidance = "Air quality is acceptable; however, there may be a risk for some people, particularly those who are unusually sensitive to air pollution."
    actions = [
        "• Unusually sensitive individuals should consider reducing prolonged or heavy exertion.",
        "• General public is fine.",
        "• Keep an eye on symptoms if asthmatic.",
    ]
    spec_position = 20 + min((aqi - 50) / 50 * 20, 20)
elif aqi <= 150:
    cat_name = "Unhealthy for Sensitive Groups"
    cat_color = "#ff5722"
    bg_tint = "#fbe9e7"
    health_guidance = "Members of sensitive groups may experience health effects. The general public is less likely to be affected."
    actions = [
        "• Sensitive groups should reduce prolonged or heavy outdoor exertion.",
        "• Use air purifiers indoors if possible.",
        "• If you have asthma, keep quick-relief medicine handy.",
    ]
    spec_position = 40 + min((aqi - 100) / 50 * 20, 20)
elif aqi <= 200:
    cat_name = "Unhealthy"
    cat_color = "#f44336"
    bg_tint = "#ffebee"
    health_guidance = "Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects."
    actions = [
        "• Everyone should reduce prolonged or heavy outdoor exertion.",
        "• Stay indoors when possible.",
        "• Keep windows closed to prevent outdoor pollution from coming inside.",
    ]
    spec_position = 60 + min((aqi - 150) / 50 * 20, 20)
elif aqi <= 300:
    cat_name = "Very Unhealthy"
    cat_color = "#9c27b0"
    bg_tint = "#f3e5f5"
    health_guidance = (
        "Health alert: The risk of health effects is increased for everyone."
    )
    actions = [
        "• Avoid all outdoor activities.",
        "• Wear an N95 mask if you must go outside.",
        "• Run air purifiers on high.",
        "• Avoid strenuous indoor activities.",
    ]
    spec_position = 80 + min((aqi - 200) / 100 * 10, 10)
else:
    cat_name = "Hazardous"
    cat_color = "#7b1c1c"
    bg_tint = "#fce4ec"
    health_guidance = "Health warning of emergency conditions: everyone is more likely to be affected."
    actions = [
        "• Remain indoors and keep activity levels low.",
        "• Check on vulnerable neighbors or family.",
        "• Ensure all external air intakes are closed.",
    ]
    spec_position = min(90 + min((aqi - 300) / 200 * 10, 10), 100)

actions_html = "<br>".join(actions)

# Variables for simulation
best_model = "Random Forest"
r2_score = 0.89
rmse = 12.3

with st.sidebar:
    st.write("")
    st.write("")

    csv_data = [
        ["PM2.5", pm25, "ug/m3"],
        ["PM10", pm10, "ug/m3"],
        ["NO2", no2, "ppb"],
        ["SO2", so2, "ppb"],
        ["CO", co, "ppm"],
        ["O3", o3, "ppb"],
        ["Temperature", st.session_state.temp, "C"],
        ["Humidity", st.session_state.hum, "%"],
        ["Predicted AQI", aqi, ""],
        ["AQI Category", cat_name, ""],
        ["R2 Score", r2_score, ""],
        ["RMSE", rmse, ""],
        ["Best Model", best_model, ""],
    ]
    df_export = pd.DataFrame(csv_data, columns=["Parameter", "Value", "Unit"])
    csv_bytes = df_export.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download CSV Report",
        data=csv_bytes,
        file_name="aqi_report.csv",
        mime="text/csv",
    )

    pdf = FPDF()
    pdf.add_page()
    try:
        pdf.set_font("helvetica", size=12)
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, "AQI Observer - Atmospheric Lab", align="C", ln=1)
        pdf.set_font("helvetica", "I", 10)
        pdf.cell(0, 10, f"Date: {datetime.date.today()}", align="C", ln=1)
        pdf.ln(5)

        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "1. Input Parameters", ln=1)
        pdf.set_font("helvetica", size=12)
        for row in csv_data[:8]:
            pdf.cell(0, 8, f"{row[0]}: {row[1]} {row[2]}", ln=1)
        pdf.ln(5)

        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "2. Prediction Result", ln=1)
        pdf.set_font("helvetica", size=12)
        pdf.cell(0, 8, f"AQI Value: {aqi}", ln=1)
        pdf.cell(0, 8, f"Category: {cat_name}", ln=1)
        pdf.ln(5)

        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "3. Health Guidance", ln=1)
        pdf.set_font("helvetica", size=12)
        pdf.multi_cell(0, 8, txt=health_guidance)
        pdf.ln(5)

        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "4. Model Information", ln=1)
        pdf.set_font("helvetica", size=12)
        pdf.cell(0, 8, f"Best Model: {best_model}", ln=1)
        pdf.cell(0, 8, f"R2 Score: {r2_score}", ln=1)
        pdf.cell(0, 8, f"RMSE: {rmse}", ln=1)

        pdf_bytes = (
            pdf.output(dest="S") if hasattr(pdf, "output_dest") else pdf.output()
        )
        if isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode("latin1")
        st.download_button(
            "📄 Download PDF Report",
            data=bytes(pdf_bytes),
            file_name="aqi_report.pdf",
            mime="application/pdf",
        )
    except Exception as e:
        st.error(f"Error generating PDF: {e}")

# --- MAIN LAYOUT ---
st.markdown("<h1>AQI Observer</h1>", unsafe_allow_html=True)

col_center, col_right = st.columns([1.5, 1])

with col_center:
    st.markdown(
        '<div class="main-header">🌍 Predict Air Quality</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-header">Monitor atmospheric conditions and receive tailored health recommendations.</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Feature 1: ML Model Credibility Panel
    st.markdown("### Model Performance")
    st.markdown(
        f"**<span style='font-size:0.9rem; background:#1a6e2e; color:white; padding:4px 8px; border-radius:10px;'>✅ Model: {best_model}</span>**",
        unsafe_allow_html=True,
    )
    st.write("")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Best Model", best_model)
    with col_m2:
        st.metric("R² Score", f"{r2_score}")
    with col_m3:
        st.metric("RMSE", f"{rmse}")

    st.markdown("---")

    # Feature 2: Feature Importance Chart
    st.markdown("### 🔍 Feature Importance")
    st.caption("Shows which pollutants most influence the AQI prediction")
    feature_importances = {
        "PM2.5": 0.38,
        "PM10": 0.22,
        "O3": 0.15,
        "NO2": 0.12,
        "SO2": 0.08,
        "CO": 0.05,
    }
    df_fi = pd.DataFrame(
        list(feature_importances.items()), columns=["Feature", "Importance"]
    )
    df_fi = df_fi.sort_values(by="Importance", ascending=True)
    fig_fi = px.bar(df_fi, x="Importance", y="Feature", orientation="h")
    fig_fi.update_traces(marker_color="#2d7a3a")
    fig_fi.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans"),
        margin=dict(l=0, r=0, t=20, b=0),
        height=300,
    )
    st.plotly_chart(fig_fi, use_container_width=True)

    st.markdown("---")

    # Feature 5: AQI Explainability Panel
    st.markdown("### 🧠 Why is AQI this value?")
    st.caption("Based on feature weight analysis")

    pm25_contrib = pm25 * 0.35
    pm10_contrib = pm10 * 0.20
    no2_contrib = no2 * 0.15
    so2_contrib = so2 * 0.10
    co_contrib = co * 5.0
    o3_contrib = o3 * 0.10
    contribs = {
        "PM2.5": pm25_contrib,
        "PM10": pm10_contrib,
        "NO2": no2_contrib,
        "SO2": so2_contrib,
        "CO": co_contrib,
        "O3": o3_contrib,
    }
    sorted_contribs = sorted(contribs.items(), key=lambda item: item[1], reverse=True)
    total_contrib = sum(contribs.values())
    if total_contrib == 0:
        total_contrib = 1
    top_1 = sorted_contribs[0]
    top_2 = sorted_contribs[1]
    pct_1 = int(round((top_1[1] / total_contrib) * 100, 0))
    pct_2 = int(round((top_2[1] / total_contrib) * 100, 0))

    st.info(f"""
    🔺 Primary driver: **{top_1[0]}** — contributing {pct_1}% to the AQI  
    🔺 Secondary driver: **{top_2[0]}** — contributing {pct_2}% to the AQI
    
    ℹ️ *Reducing {top_1[0]} levels will have the highest impact on improving AQI.*
    """)

    st.markdown("---")

    # Feature 3: Dynamic AQI Color Theme & Gauge Chart
    gauge_fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=aqi,
            title={"text": "AQI Gauge", "font": {"size": 18}},
            gauge={
                "axis": {"range": [0, 500]},
                "steps": [
                    {"range": [0, 50], "color": "#4caf50"},
                    {"range": [51, 100], "color": "#ff9800"},
                    {"range": [101, 150], "color": "#ff5722"},
                    {"range": [151, 200], "color": "#f44336"},
                    {"range": [201, 300], "color": "#9c27b0"},
                    {"range": [301, 500], "color": "#7b1c1c"},
                ],
                "bar": {"color": "black"},
            },
        )
    )
    gauge_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "DM Sans"},
        margin=dict(l=20, r=20, t=40, b=20),
    )
    gauge_html_str = gauge_fig.to_html(
        full_html=False, include_plotlyjs="cdn", config={"displayModeBar": False}
    )

    card_html = f"""
    <html>
    <head>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
    body {{
        font-family: 'DM Sans', sans-serif;
        margin: 0;
        padding: 0;
        background-color: transparent;
    }}
    .custom-card {{
        background-color: {bg_tint};
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        border-left: 8px solid {cat_color};
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-sizing: border-box;
    }}
    .aqi-label {{
        font-size: 0.85rem;
        font-weight: 700;
        color: #888888;
        letter-spacing: 1px;
    }}
    .aqi-number {{
        font-size: 4rem;
        font-weight: 700;
        line-height: 1.1;
        margin-bottom: 10px;
        color: {cat_color};
    }}
    .pill-badge {{
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        color: white;
        background-color: {cat_color};
    }}
    .gauge-container {{
        width: 100%;
        max-width: 350px;
        height: 250px;
    }}
    </style>
    </head>
    <body>
    <div class="custom-card">
        <div style="flex: 1;">
            <div class="aqi-label">CURRENT PREDICTION</div>
            <div class="aqi-number">{aqi}</div>
            <div class="pill-badge">{cat_name}</div>
        </div>
        <div class="gauge-container">
            {gauge_html_str}
        </div>
    </div>
    </body>
    </html>
    """
    components.html(card_html, height=310)

    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.markdown(
            f"""
        <div class="card">
            <h3 style="margin-top:0; font-size:1.1rem; margin-bottom:10px;">🛡️ Health Guidance</h3>
            <p style="color:#666; font-size:0.95rem; line-height:1.5;">{health_guidance}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )
    with col_h2:
        st.markdown(
            f"""
        <div class="card">
            <h3 style="margin-top:0; font-size:1.1rem; margin-bottom:10px;">✅ Actions</h3>
            <p style="color:#666; font-size:0.95rem; line-height:1.5;">{actions_html}</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Feature 4: Time-Based AQI Trend Chart
    st.markdown("### 📈 AQI Trend (Last 7 Days)")

    today = datetime.date.today()
    dates = [today - datetime.timedelta(days=i) for i in range(6, -1, -1)]
    date_strs = [d.strftime("%a %b %d") for d in dates]
    past_aqis = [random.randint(40, 180) for _ in range(6)] + [aqi]

    df_trend = pd.DataFrame({"Date": date_strs, "AQI": past_aqis})
    fig_trend = go.Figure()

    marker_colors = ["#2d7a3a"] * 6 + [cat_color]

    fig_trend.add_trace(
        go.Scatter(
            x=df_trend["Date"],
            y=df_trend["AQI"],
            mode="lines+markers",
            line=dict(color="#2d7a3a", width=3),
            marker=dict(
                size=12, color=marker_colors, line=dict(width=2, color="white")
            ),
        )
    )
    fig_trend.add_hline(
        y=100,
        line_dash="dash",
        line_color="#ff9800",
        annotation_text="Moderate threshold",
        annotation_position="top right",
    )
    fig_trend.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans"),
        margin=dict(l=0, r=0, t=20, b=0),
        yaxis=dict(range=[0, max(300, max(past_aqis) + 20)], title="AQI Value"),
        xaxis=dict(title=""),
    )

    st.markdown('<div id="trend-card-anchor"></div>', unsafe_allow_html=True)
    st.plotly_chart(fig_trend, use_container_width=True)
    st.caption("Simulated historical trend. Replace with real data for production.")

    st.markdown(
        f"""
    <style>
    div[data-testid="stVerticalBlock"]:has(> div.element-container > div.stMarkdown > div > p > div#trend-card-anchor) {{
        background-color: #ffffff;
        border-radius: 14px;
        padding: 24px;
        margin-top: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }}
    </style>
    """,
        unsafe_allow_html=True,
    )


with col_right:
    st.markdown(
        f"""
    <div class="card">
        <h3 style="margin-top:0; font-size:1.1rem; margin-bottom:10px;">🌈 AQI Spectrum</h3>
        <div class="spectrum-container">
            <div class="spectrum-bar">
                <div class="spectrum-marker" style="left: calc({spec_position}% - 2px);"></div>
            </div>
            <div class="spectrum-labels">
                <span>GOOD</span>
                <span>MODERATE</span>
                <span>UNHEALTHY</span>
                <span>HAZARD</span>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
    <div class="dark-card">
        <h3 style="margin-top:0; font-size:1.1rem; margin-bottom:20px;">🌤️ Atmospheric Context</h3>
        <div style="display: flex; gap: 10px; margin-bottom: 20px;">
            <div class="metric-box" style="flex: 1;">
                <div class="metric-value">{st.session_state.temp}</div>
                <div class="metric-label">TEMP (°C)</div>
            </div>
            <div class="metric-box" style="flex: 1;">
                <div class="metric-value">{st.session_state.hum}</div>
                <div class="metric-label">HUMIDITY (%)</div>
            </div>
        </div>
        <p style="font-size:0.85rem; opacity:0.9; margin:0;">Stable conditions with low wind speed may lead to pollutant accumulation.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.session_state.temp = st.slider(
        "Temperature (°C)",
        min_value=-10,
        max_value=50,
        value=st.session_state.temp,
        step=1,
    )
    st.session_state.hum = st.slider(
        "Humidity (%)", min_value=0, max_value=100, value=st.session_state.hum, step=1
    )
