import streamlit as st
import joblib
import requests
import pandas as pd

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Environmental AI Platform",
    layout="wide",
    page_icon="🌤"
)

# ===============================
# FULL HERO BACKGROUND STYLE
# ===============================
st.markdown("""
<style>
/* Full background image */
.stApp {
    background-image: url("https://images.unsplash.com/photo-1501973801540-537f08ccae7b");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}

/* Overlay for better readability */
.block-container {
    background: rgba(0, 0, 0, 0.55);
    padding: 40px;
    border-radius: 20px;
}

/* Title */
.title {
    font-size: 48px;
    font-weight: 700;
    color: white;
    text-align: center;
}

/* Subtitle */
.subtitle {
    font-size: 18px;
    color: #e0e0e0;
    text-align: center;
    margin-bottom: 40px;
}

/* AQI Big Number */
.aqi-number {
    font-size: 80px;
    font-weight: 800;
    text-align: center;
    margin-bottom: 10px;
}

/* Status */
.status {
    font-size: 22px;
    text-align: center;
    margin-bottom: 30px;
}

/* Category Colors */
.good { color: #00E676; }
.moderate { color: #FFC107; }
.poor { color: #FF5252; }

/* Pollutant card */
.pollutant-card {
    background: rgba(255,255,255,0.1);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    color: white;
}

/* Button styling */
div.stButton > button {
    background-color: #ff6b35;
    color: white;
    border-radius: 30px;
    height: 50px;
    width: 200px;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# LOAD MODEL
# ===============================
model = joblib.load("pm25_model.pkl")

API_KEY = "c1d0350bfa5a98806e970e1003914936"  # Replace

# ===============================
# HEADER
# ===============================
st.markdown('<div class="title">Smarter Air Quality Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Based Real-Time Environmental Monitoring System</div>', unsafe_allow_html=True)

# ===============================
# CITY SELECT
# ===============================
cities = {
    "Coimbatore": (11.0168, 76.9558),
    "Chennai": (13.0827, 80.2707),
    "Delhi": (28.7041, 77.1025),
    "Mumbai": (19.0760, 72.8777),
    "Bangalore": (12.9716, 77.5946)
}

selected_city = st.selectbox("Select City", list(cities.keys()))
lat, lon = cities[selected_city]

# ===============================
# CATEGORY FUNCTION
# ===============================
def get_category(aqi):
    if aqi <= 50:
        return "Good", "good"
    elif aqi <= 100:
        return "Moderate", "moderate"
    else:
        return "Poor", "poor"

# ===============================
# FETCH & PREDICT
# ===============================
if st.button("Analyze Air Quality"):

    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "list" not in data:
        st.error("Unable to fetch data. Check API key.")
    else:
        components = data["list"][0]["components"]

        so2 = components.get("so2", 0)
        no2 = components.get("no2", 0)
        pm10 = components.get("pm10", 0)
        pm25 = components.get("pm2_5", 0)

        input_data = pd.DataFrame([{
            "SO2": so2,
            "NO2": no2,
            "RSPM/PM10": pm10,
            "PM 2.5": pm25
        }])

        for col in model.feature_names_in_:
            if col not in input_data.columns:
                input_data[col] = 0

        input_data = input_data[model.feature_names_in_]

        predicted_aqi = model.predict(input_data)[0]
        category, css_class = get_category(predicted_aqi)

        # Display AQI
        st.markdown(
            f'<div class="aqi-number {css_class}">{round(predicted_aqi)}</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="status {css_class}">{category} Air Quality</div>',
            unsafe_allow_html=True
        )

        # Pollutants
        col1, col2, col3, col4 = st.columns(4)

        col1.markdown(f'<div class="pollutant-card">PM2.5<br><b>{pm25}</b></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="pollutant-card">PM10<br><b>{pm10}</b></div>', unsafe_allow_html=True)
        col3.markdown(f'<div class="pollutant-card">NO₂<br><b>{no2}</b></div>', unsafe_allow_html=True)
        col4.markdown(f'<div class="pollutant-card">SO₂<br><b>{so2}</b></div>', unsafe_allow_html=True)