import streamlit as st
import requests
import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import time
import json


st.set_page_config(
    page_title="📊 ISS Analytics",
    page_icon="📊",
    layout="wide"
)

# Custom CSS (matching AURA theme)
st.markdown("""
<style>
    .analytics-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #2a5298 0%, #1e3c72 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .orbital-stats {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Simulated ISS orbital data functions
@st.cache_data(ttl=300)  # Cache for 5m
def get_extended_iss_data():
    """Get ISS data w simulated orbital params"""
    try:
        response = requests.get("http://api.open-notify.org/iss-now.json", timeout=10)
        response.raise_for_status()
        data = response.json()

        # Add simulated orbital data
        iss_data = {
            'latitude': float(data["iss_position"]["latitude"]),
            'longitude': float(data["iss_position"]["longitude"]),
            'timestamp': datetime.fromtimestamp(data["timestamp"]),
            # Simulated data for demo purposes
            'altitude_km': 408,  # Average ISS altitude
            'velocity_kmh': 27580,  # Average ISS velocity
            'orbital_period_min': 93,  # Time for one orbit
            'solar_panel_angle': np.random.randint(0, 180),
            'power_generation_kw': np.random.uniform(75, 120),
            'crew_count': 7,  # Current typical crew size
        }

        return iss_data
    except Exception as e:
        st.error(f"Error fetching ISS data: {e}")
        return None


