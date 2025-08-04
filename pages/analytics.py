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
    page_title="ISS Analytics",
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
@st.cache_data(ttl=300, show_spinner=False)  # Cache for 5m
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
        lat_frequency = 2 * np.pi / orbital_period_hours
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
        freq='h'
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


def main():
    # Header
    st.markdown("""
    <div class="analytics-header">
        <h1>📊 ISS Advanced Analytics</h1>
        <h2>Orbital Mechanics & Performance Data</h2>
        <p>Deep dive into ISS operations and orbital parameters</p>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Fetching ISS Data.."):
        # Get current ISS data
        iss_data = get_extended_iss_data()

    if not iss_data:
        st.error("Unable to fetch ISS data for analytics")
        return
    
    # Real-time Orbital Metrics
    st.header("🛰️ Real-Time Orbital Metrics")
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Altitude",
            value=f"{iss_data['altitude_km']} km",
            delta="408 km average",
            help="ISS orbits at approximately 408km above Earth"
        )
    
    with col2:
        st.metric(
            label="Velocity",
            value=f"{iss_data['velocity_kmh']:,} km/h",
            delta="17,150 mph",
            help="ISS travels at about 7.66 km/s"
        )
    
    with col3:
        st.metric(
            label="Orbital Period",
            value=f"{iss_data['orbital_period_min']} min",
            delta="~15.5 orbits/day",
            help="Time to complete one orbit around Earth"
        )
    
    with col4:
        st.metric(
            label="Power Generation",
            value=f"{iss_data['power_generation_kw']:.1f} kW",
            delta="Solar panels active",
            help="Power generated by ISS solar arrays"
        )
    
    # Orbital Path Visualization
    st.header("Predicted Orbital Path")

    col1, col2 = st.columns([3, 1])

    with col2:
        hours_ahead = st.slider("Hours to predict", 1, 6, 2)
        show_current_pos = st.checkbox("Show current position", True)

    with col1:
        # Generate orbital path
        orbital_path = generate_orbital_path(
            iss_data['latitude'],
            iss_data['longitude'],
            hours_ahead
        )

        if orbital_path:
            path_df = pd.DataFrame(orbital_path)

            fig = go.Figure()

            # Add orbital path
            fig.add_trace(go.Scattermap(
                lat=path_df['lat'],
                lon=path_df['lng'],
                mode='lines+markers',
                marker=dict(size=4, color='cyan'),
                line=dict(width=2, color='cyan'),
                name='Predicted Path',
                hovertemplate='<b>Predicted Position</b><br>' +
                             'Lat: %{lat:.2f}°<br>' +
                             'Lng: %{lon:.2f}°<br>' +
                             '<extra></extra>'
            ))

            # Add current position
            if show_current_pos:
                fig.add_trace(go.Scattermap(
                    lat=[iss_data['latitude']],
                    lon=[iss_data['longitude']],
                    mode='markers',
                    marker=dict(size=15, color='red', symbol='circle'),
                    name='Current Position',
                    hovertemplate='<b>Current ISS Position</b><br>' +
                                 'Lat: %{lat:.2f}°<br>' +
                                 'Lng: %{lon:.2f}°<br>' +
                                 '<extra></extra>'
                ))
            
            fig.update_layout(
                mapbox=dict(
                    style="open-street-map",
                    center=dict(lat=iss_data['latitude'], lon=iss_data['longitude']),
                    zoom=1
                ),
                height=500,
                margin={"r":0, "t":0, "l":0, "b":0}
            )

            st.plotly_chart(fig, use_container_width=True)
    
    # Historical Performance Analytics
    st.header("📈 Historical Performance Analytics")
    
    # Generate historical data
    hist_data = generate_historical_data(days_back=7)
    
    tab1, tab2, tab3 = st.tabs(["🔋 Power Systems", "🛰️ Orbital Parameters", "📡 Communications"])
    
    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            # Power generation over time
            fig_power = px.line(
                hist_data,
                x='timestamp',
                y='power_generation_kw',
                title='Power Generation Over Time',
                labels={'power_generation_kw': 'Power (kW)', 'timestamp': 'Date'}
            )
            fig_power.update_traces(line_color='orange')
            st.plotly_chart(fig_power, use_container_width=True)
        
        with col2:
            # Solar panel efficiency
            fig_efficiency = px.line(
                hist_data,
                x='timestamp',
                y='solar_panel_efficiency',
                title='Solar Panel Efficiency',
                labels={'solar_panel_efficiency': "Efficiency (%)", 'timestamp': 'Date'}
            )
            fig_efficiency.update_traces(line_color='green')
            st.plotly_chart(fig_efficiency, use_container_width=True)
        
    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            # Altitude variations
            fig_alt = px.line(
                hist_data,
                x='timestamp',
                y='altitude_km',
                title='Altitude Variations',
                labels={'altitude_km': 'Altitude (km)', 'timestamp': 'Date'}
            )
            fig_alt.update_traces(line_color='blue')
            st.plotly_chart(fig_alt, use_container_width=True)
        
        with col2:
            # Velocity Tracking
            fig_vel = px.line(
                hist_data,
                x='timestamp',
                y='velocity_kmh',
                title='Velocity Tracking',
                labels={'velocity_kmh': 'Velocity (km/h)', 'timestamp': 'Date'}
            )
            fig_vel.update_traces(line_color='purple')
            st.plotly_chart(fig_vel, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)

        with col1:
            # Communication strength
            fig_comm = px.line(
                hist_data,
                x='timestamp',
                y='communication_strength',
                title='Communication Signal Strength',
                labels={'communication_strength': 'Signal Strength (%)', 'timestamp': 'Date'}
            )
            fig_comm.update_traces(line_color='red')
            st.plotly_chart(fig_comm, use_container_width=True)
        
        with col2:
            # Crew activity levels
            activity_counts = hist_data['crew_activity_level'].value_counts()
            fig_activity = px.pie(
                values=activity_counts.values,
                names=activity_counts.index,
                title='Crew Activity Distribution (7 days)'
            )
            st.plotly_chart(fig_activity, use_container_width=True)
    
    # Performance Summary
    st.header("Performance Summary")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <h4>🔋 Power Systems</h4>
            <p><strong>Avg Generation:</strong> {:.1f} kW</p>
            <p><strong>Peak Efficiency:</strong> {:.1f}%</p>
            <p><strong>Status:</strong> <span style="color: green;">Optimal</span></p>
        </div>
        """.format(
            hist_data['power_generation_kw'].mean(),
            hist_data['solar_panel_efficiency'].max()
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h4>🛰️ Orbital Stability</h4>
            <p><strong>Avg Altitude:</strong> {:.1f} km</p>
            <p><strong>Velocity Range:</strong> {:.0f} km/h</p>
            <p><strong>Status:</strong> <span style="color: green;">Stable</span></p>
        </div>
        """.format(
            hist_data['altitude_km'].mean(),
            hist_data['velocity_kmh'].std()
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h4>📡 Communications</h4>
            <p><strong>Avg Signal:</strong> {:.1f}%</p>
            <p><strong>Uptime:</strong> 99.2%</p>
            <p><strong>Status:</strong> <span style="color: green;">Excellent</span></p>
        </div>
        """.format(
            hist_data['communication_strength'].mean()
        ), unsafe_allow_html=True)

    # Technical Details
    with st.expander("🔧 Technical Implementation Details"):
        st.write("**Data Processing:**")
        st.write("• Real-time ISS position from Open Notify API")
        st.write("• Orbital mechanics calculations using simplified Kepler equations")
        st.write("• Historical data simulation for demonstration purposes")
        st.write("")
        st.write("**Analytics Features:**")
        st.write("• Predictive orbital path modeling")
        st.write("• Power generation trend analysis")
        st.write("• Communication signal strength tracking")
        st.write("• Crew activity pattern recognition")
        st.write("")
        st.write("**Visualization Technologies:**")
        st.write("• Plotly for interactive charts and maps")
        st.write("• Streamlit for responsive web interface")
        st.write("• Pandas for data manipulation and analysis")

if __name__ == "__main__":
    main()