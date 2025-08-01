import streamlit as st
import pandas as pd 
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
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