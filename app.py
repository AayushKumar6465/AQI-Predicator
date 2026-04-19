import streamlit as st

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
    health_guidance = "Air quality is acceptable; however, there may be a risk for some people, particularly those who are unusually sensitive to air pollution."
    actions = [
        "• Unusually sensitive individuals should consider reducing prolonged or heavy exertion.",
        "• General public is fine.",
        "• Keep an eye on symptoms if asthmatic.",
    ]
    spec_position = 20 + min((aqi - 50) / 50 * 20, 20)
elif aqi <= 150:
    cat_name = "Unhealthy for Sensitive Groups"
    cat_color = "#ff9800"
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
    health_guidance = "Health warning of emergency conditions: everyone is more likely to be affected."
    actions = [
        "• Remain indoors and keep activity levels low.",
        "• Check on vulnerable neighbors or family.",
        "• Ensure all external air intakes are closed.",
    ]
    spec_position = min(90 + min((aqi - 300) / 200 * 10, 10), 100)

actions_html = "<br>".join(actions)

report_text = f"""--- AQI Observer Report ---
Overall AQI: {aqi} ({cat_name})

Pollutant Levels:
- PM2.5: {pm25} µg/m³
- PM10: {pm10} µg/m³
- NO₂: {no2} ppb
- SO₂: {so2} ppb
- CO: {co} ppm
- O₃: {o3} ppb

Atmospheric Context:
- Temperature: {st.session_state.temp}°C
- Humidity: {st.session_state.hum}%

Health Guidance:
{health_guidance}

Recommended Actions:
{chr(10).join(act.strip() for act in actions)}
---------------------------"""

with st.sidebar:
    st.write("")
    st.write("")
    st.download_button(
        label="Share Report",
        data=report_text,
        file_name="aqi_observer_report.txt",
        mime="text/plain",
    )

# --- MAIN LAYOUT ---
st.markdown("<h1>AQI Observer</h1>", unsafe_allow_html=True)

col_center, col_right = st.columns([1.5, 1])

with col_center:
    col_c1, col_c2 = st.columns([3, 1])
    with col_c1:
        st.markdown(
            '<div class="main-header">🌍 Predict Air Quality</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="sub-header">Monitor atmospheric conditions and receive tailored health recommendations.</div>',
            unsafe_allow_html=True,
        )
    with col_c2:
        st.write("")
        st.button("⚡ Predict AQI")

    st.markdown(
        f"""
    <div class="card prediction-card" style="border-left-color: {cat_color};">
        <div class="aqi-label">CURRENT PREDICTION</div>
        <div class="aqi-number" style="color: {cat_color};">{aqi}</div>
        <div class="pill-badge" style="background-color: {cat_color};">{cat_name}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

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
