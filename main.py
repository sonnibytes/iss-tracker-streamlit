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


# Main App
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🛰️ International Space Station</h1>
        <h2>Real-Time Tracking Dashboard</h2>
        <p>Live position, astronaut info, and visibility predictions</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar for user location
    st.sidebar.header("📍 Your Location")

    # Default to my location in Mobile, AL
    user_lat = st.sidebar.number_input("Latitude", value=30.673290, format="%.6f")
    user_lng = st.sidebar.number_input("Longitude", value=-88.111153, format="%.6f")
    
    # Add some preset locations
    preset_locations = {
        "Mobile, AL": (30.673290, -88.111153),
        "New York City": (40.7128, -74.0060),
        "Los Angeles": (34.0522, -118.2437),
        "London": (51.5074, -0.1278),
        "Tokyo": (35.6762, 139.6503),
        "Sydney": (-33.8688, 151.2093)
    }

    selected_location = st.sidebar.selectbox("Or choose a preset:", list(preset_locations.keys()))
    if st.sidebar.button("Use Preset Location"):
        user_lat, user_lng = preset_locations[selected_location]
        st.rerun()
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto-refresh (60s)", value=True)

    if auto_refresh:
        # Auto-refresh every 60 seconds
        time.sleep(1)
        st.rerun()
    
    # Manual refresh button
    if st.sidebar.button("Refresh Now"):
        st.cache_data.clear()
        st.rerun()
    
    # Get ISS Data
    iss_location = get_iss_location()
    astronaut_data = get_astronauts()

    if not iss_location:
        st.error("Unable to fetch ISS data. Please check your connection and try again.")
        return
    
    # Current ISS Status
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Latitude",
            value=f"{iss_location['latitude']:.4f}°",
            help="Current ISS latitude position"
        )
    
    with col2:
        st.metric(
            label="Longitude",
            value=f"{iss_location['longitude']:.4f}°",
            help="Current ISS longitude position"
        )
    
    with col3:
        if astronaut_data:
            st.metric(
                label="Astronauts",
                value=astronaut_data['count'],
                help="People currently aboard the ISS"
            )
        else:
            st.metric(label="Astronauts", value="Error")
    
    with col4:
        # Calculate distance from user
        distance = math.sqrt((iss_location['latitude'] - user_lat)**2 + (iss_location['longitude'] - user_lng)**2)

        st.metric(
            label="Distance",
            value=f"{distance:.1f}°",
            help="Angular distance from your location"
        )
    
    # ISS World Map
    st.subheader("Live ISS Position")

    # Create map data
    map_data = pd.DataFrame({
        'lat': [iss_location['latitude'], user_lat],
        'lon': [iss_location['longitude'], user_lng],
        'name': ['🛰️ ISS', '📍 You'],
        'size': [20, 15]
    })

    # Create plotly map
    fig = px.scatter_mapbox(
        map_data,
        lat="lat",
        lon='"lon',
        hover_name="name",
        size="size",
        zoom=1,
        mapbox_style="open-street-map",
        height=400
    )

    fig.update_layout(
        margin={"r":0, "t":0, "l":0, "b":0},
        mapbox=dict(
            center=dict(lat=iss_location['latitude'], lon=iss_location['longitude'])
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # Visibility Check
    st.subheader("Visibility Status")

    # Get sunrise/sunset data
    sun_data = get_sunrise_sunset(user_lat, user_lng)
    is_nearby = is_iss_nearby(iss_location['latitude'], iss_location['longitude'],
                              user_lat, user_lng)
    is_dark = is_nighttime(sun_data) if sun_data else False

    col1, col2 = st.columns(2)

    with col1:
        if is_nearby:
            st.success("🎯 ISS is nearby! (±5° from your location)")
        else:
            st.info("🌍 ISS is not currently nearby")
        
        if is_dark:
            st.success("🌙 It's dark at your location")
        else:
            st.info("☀️ It's daylight at your location")
    
    with col2:
        if is_nearby and is_dark:
            st.success("🔭 **LOOK UP! ISS might be visible!**")
        else:
            st.info("⏳ ISS not currently visible from your location")
        
        if sun_data:
            st.write(f"Sunrise: {sun_data['sunrise'].strftime('%I:%M %p')}")
            st.write(f"Sunset: {sun_data['sunset'].strftime('%I:%M %p')}")
    
    # Upcoming passes
    st.subheader("Upcoming ISS Passes")

    passes = get_iss_passes(user_lat, user_lng)
    if passes:
        pass_data = []
        for i, pass_info in enumerate(passes):
            pass_data.append({
                "Pass #": i + 1,
                "Date": pass_info['date'].strftime('%Y-%m-%d'),
                "Time": pass_info['date'].strftime('%I:%M %p'),
                "Duration": f"{pass_info['duration'] // 60}m {pass_info['duration'] % 60}s",
                "Days Away": (pass_info['date'].date() - datetime.now().date()).days
            })
        
        df_passes = pd.DataFrame(pass_data)
        st.dataframe(df_passes, use_container_width=True)
    else:
        st.warning("Unable to fetch pass prediction data")
    
    


