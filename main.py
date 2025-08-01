import streamlit as st
import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import time
import math
import json

# Page config
st.set_page_config(
    page_title="🛰️ ISS Real-Time Tracker",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for AURA theme
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .metric-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .status-good { color: #10B981; }
    .status-warning { color: #F59E0B; }
    .status-info { color: #3B82F6; }
    
    .iss-info {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ISS API functions
@st.cache_data(ttl=60)  # Cache for 1min
def get_iss_location():
    """Get current position of ISS"""
    try:
        response = requests.get("http://api.open-notify.org/iss-now.json", timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            'latitude': float(data['iss_position']['latitude']),
            'longitude': float(data['iss_position']['longitude']),
            'timestamp': datetime.fromtimestamp(data['timestamp'])
        }
    except Exception as e:
        st.error(f"Error fetching ISS location: {e}")
        return None

@st.cache_data(ttl=3600)  # Cache for 1h
def get_astronauts():
    """Get current astronauts in space"""
    try:
        response = requests.get("http://api.open-notify.org/astros.json", timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            'count': data['number'],
            'astronauts': data['people']
        }
    except Exception as e:
        st.error(f"Error fetching astronaut data: {e}")
        return None


@st.cache_data(ttl=3600)  # Cache for 1h
def get_iss_passes(lat, lng, alt=0, n=5):
    """Get upcoming ISS passes for a location"""
    try:
        url = "http://api.open-notify.org/iss-pass.json"
        params = {
            'lat': lat,
            'lon': lng,
            'alt': alt,
            'n': n
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        passes = []
        for pass_info in data['response']:
            passes.append({
                'date': datetime.fromtimestamp(pass_info['risetime']),
                'duration': pass_info['duration']
            })

        return passes
    except Exception as e:
        st.error(f"Error fetching pass data: {e}")
        return []


def get_sunrise_sunset(lat, lng):
    """Get sunrise/sunset times for location"""
    try:
        params = {
            "lat": lat,
            "lng": lng,
            "formatted": 0,
        }
        response = requests.get("https://api.sunrise-sunset.org/json", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            'sunrise': datetime.fromisoformat(data['results']['sunrise'].replace('Z', '+00:00')),
            'sunset': datetime.fromisoformat(data['results']['sunset'].replace('Z', '+00:00'))
        }
    except Exception as e:
        st.error(f"Error fetching sunrise/sunset data: {e}")
        return None


def is_iss_nearby(iss_lat, iss_lng, user_lat, user_lng, tolerance=5):
    """Check if ISS is nearby user location"""
    return (math.isclose(iss_lat, user_lat, abs_tol=tolerance) and math.isclose(iss_lng, user_lng, abs_tol=tolerance))


def is_nighttime(sunrise_sunset_data):
    """Check if it's currently nighttime"""
    if not sunrise_sunset_data:
        return False
    
    now = datetime.now(sunrise_sunset_data['sunrise'].tzinfo)
    sunrise = sunrise_sunset_data['sunrise']
    sunset = sunrise_sunset_data['sunset']

    # If sunset is after sunrise (normal day)
    if sunset > sunrise:
        return now < sunrise or now > sunset
    # If sunset is before sunrise (crosses midnight)
    else:
        return now > sunset and now < sunrise





