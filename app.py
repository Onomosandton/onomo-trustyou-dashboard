import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
import base64
import os
import json
from datetime import datetime, timedelta

# 1. Page Configuration
st.set_page_config(page_title="Executive Command Center", layout="wide", initial_sidebar_state="expanded")

# 2. Local Storage for GM Targets
TARGETS_FILE = "gm_targets.json"

def load_targets():
    if os.path.exists(TARGETS_FILE):
        with open(TARGETS_FILE, "r") as f:
            return json.load(f)
    return {"TrustYou Survey": 85, "booking.com": 85, "google.com": 85, "tripadvisor.com": 85}

def save_targets(targets):
    with open(TARGETS_FILE, "w") as f:
        json.dump(targets, f)

if 'gm_targets' not in st.session_state:
    st.session_state.gm_targets = load_targets()

# 3. Base64 Assets & CSS
def get_base64_image(filepath):
    if not os.path.exists(filepath): return ""
    with open(filepath, "rb") as f: return base64.b64encode(f.read()).decode("utf-8")

aleph_b64 = get_base64_image("aleph_logo.png")
onomo_b64 = get_base64_image("onomo_logo.jpg")

st.markdown("""
<style>
    [data-testid="stToolbar"] {display: none !important;}
    footer {display: none !important;}
    header {display: none !important;}
    .stApp { background-color: #F8F9FA; }
    h1, h2, h3, h4, h5, h6, p, span, div { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    
    div[data-testid="stFileUploader"] section { background-color: #FFFFFF !important; border: 2px dashed #7EC8BD !important; border-radius: 12px !important; padding: 20px !important; }
    div[data-testid="metric-container"] { background: #FFFFFF !important; padding: 20px; border-radius: 12px; border-top: 4px solid #7EC8BD; box-shadow: 0 10px 30px rgba(0,0,0,0.02); border: 1px solid rgba(0,0,0,0.01); }
    div[data-testid="metric-container"] label { color: #888888 !important; font-weight: 700 !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 1px; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #1A1A1A !important; font-weight: 900 !important; font-size: 2.2rem !important; }
    .glass-container { background: #FFFFFF !important; border-radius: 16px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.02); border: 1px solid rgba(0,0,0,0.01) !important; margin-bottom: 25px; }
    .section-header { font-size: 1.4rem; font-weight: 900; color: #1A1A1A; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 2px solid #F0F0F0; padding-bottom: 10px;}
</style>
""", unsafe_allow_html=True)

# 4. Data Extraction Pipelines
def fetch_live_firebase_data():
    try:
        if "firebase" not in st.secrets or "project_id" not in st.secrets["firebase"]: return pd.DataFrame()
        project_id = st.secrets["firebase"]["project_id"]
        base_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/artifacts/onomo_live_production_v1/public/data/feedback_entries"
        
        response = requests.get(base_url, params={"pageSize": 300}, timeout=4)
        if response.status_code != 200: return pd.DataFrame()
            
        documents = response.json().get("documents", [])
        records = []
        for doc in documents:
            fields = doc.get("fields", {})
            records.append({
                "guestName": str(fields.get("guestName", {}).get("stringValue", "")).strip(),
                "department": fields.get("department", {}).get("stringValue", ""),
                "reason": fields.get("reason", {}).get("stringValue", ""),
                "status": fields.get("status", {}).get("stringValue", "resolved"),
                "type": fields.get("type", {}).get("stringValue", "complaint"),
                "cost":
