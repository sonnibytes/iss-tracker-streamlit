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


def generate_orbital_path(current_lat, current_lng, hours_ahead=2):
    """Generate predicted orbital path for visualization"""
    # This is a simplified simulation - real orbital mechanics are much more complex
    path_points = []

    # ISS orbital period is about 93 minutes
    orbital_period_hours = 1.55
    points_per_orbit = 50
    total_points = int((hours_ahead / orbital_period_hours) * points_per_orbit)

    for i in range(total_points):
        # Simple simulation: ISS moves roughly 15.5 degrees per hour in longitude
        time_offset = (i / points_per_orbit) * orbital_period_hours

        # Simulate longitude movement (eastward)
        new_lng = current_lng + (time_offset * 15.5)
        if new_lng > 180:
            new_lng -= 360
        
        # Simulate latitude oscillation (between +51.6 and -51.6 degrees)
        lat_amplitude = 51.6
        lat_frequency = 2 + np.pi / orbital_period_hours
        new_lat = lat_amplitude * np.sin(lat_frequency * time_offset)

        path_points.append({
            'lat': new_lat,
            'lng': new_lng,
            'time_hours': time_offset,
            'timestamp': datetime.now() + timedelta(hours=time_offset)
        })
    
    return path_points


def generate_historical_data(days_back=7):
    """Generate simulated historical ISS data"""
    np.random.seed(42)  # For reproducible "historical" data

    dates = pd.date_range(
        start=datetime.now() - timedelta(days=days_back),
        end=datetime.now(),
        freq='H'
    )

    historical_data = []
    for date in dates:
        # Simulate varying metrics
        historical_data.append({
            'timestamp': date,
            'altitude_km': 408 + np.random.normal(0, 5),
            'velocity_kmh': 27580 + np.random.normal(0, 50),
            'power_generation_kw': 90 + np.random.normal(0, 15),
            'solar_panel_efficiency': 85 + np.random.normal(0, 8),
            'communication_strength': np.random.uniform(70, 100),
            'crew_activity_level': np.random.choice(['Low', 'Medium', 'High']),
        })
    
    return pd.DataFrame(historical_data)