import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import base64
import os
from datetime import datetime, timedelta

# 1. Page Configuration
st.set_page_config(
    page_title="Synergy Command Center",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Safe Base64 Image Loader
def get_base64_image(filepath):
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

aleph_b64 = get_base64_image("aleph_logo.png")
onomo_b64 = get_base64_image("onomo_logo.jpg")
vibe_b64 = get_base64_image("vibe1.jpg")

# 3. Silent Firebase Data Fetcher
def fetch_live_firebase_data():
    try:
        if "firebase" not in st.secrets or "project_id" not in st.secrets["firebase"]:
            return pd.DataFrame()
            
        project_id = st.secrets["firebase"]["project_id"]
        base_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/artifacts/onomo_live_production_v1/public/data/feedback_entries"
        
        response = requests.get(base_url, params={"pageSize": 300}, timeout=4)
        if response.status_code != 200:
            return pd.DataFrame()
            
        data = response.json()
        documents = data.get("documents", [])
        
        records = []
        for doc in documents:
            fields = doc.get("fields", {})
            records.append({
                "guestName": str(fields.get("guestName", {}).get("stringValue", "")).strip(),
                "department": fields.get("department", {}).get("stringValue", ""),
                "reason": fields.get("reason", {}).get("stringValue", ""),
                "status": fields.get("status", {}).get("stringValue", "resolved"),
                "type": fields.get("type", {}).get("stringValue", "complaint"),
                "cost": float(fields.get("cost", {}).get("doubleValue", fields.get("cost", {}).get("integerValue", 0))),
                "date": pd.to_datetime(fields.get("date", {}).get("stringValue", ""), errors='coerce')
            })
        return pd.DataFrame(records)
    except Exception:
        return pd.DataFrame()

# 4. Premium Design CSS
st.markdown("""
<style>
    [data-testid="stToolbar"] {display: none !important;}
    footer {display: none !important;}
    header {display: none !important;}
    .st-emotion-cache-1629p8f a, a.anchor-link {display: none !important;}
    .stApp { background-color: #F8F9FA; }
    h1, h2, h3, h4, h5, h6, p, span, div { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    
    div[data-testid="stFileUploader"] section {
        background-color: #FFFFFF !important;
        border: 2px dashed #7EC8BD !important; 
        border-radius: 12px !important;
        padding: 40px !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.02) !important;
    }
    div[data-testid="stFileUploader"] section:hover {
        background-color: #F0F9F8 !important;
        border-color: #4A5D54 !important;
    }
    
    div[data-testid="metric-container"] {
        background: #FFFFFF !important; padding: 24px; border-radius: 12px;
        border-top: 4px solid #7EC8BD; box-shadow: 0 10px 30px rgba(0,0,0,0.03); border: 1px solid rgba(0,0,0,0.02);
    }
    div[data-testid="metric-container"] label { color: #888888 !important; font-weight: 700 !important; font-size: 0.85rem !important; text-transform: uppercase; letter-spacing: 1px; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #1A1A1A !important; font-weight: 800 !important; font-size: 2.8rem !important; }
    .glass-container { background: #FFFFFF !important; border-radius: 16px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); border: 1px solid rgba(0,0,0,0.02) !important; }
</style>
""", unsafe_allow_html=True)

# 5. Header Layout
aleph_img_tag = f'<img src="data:image/png;base64,{aleph_b64}" width="160" style="mix-blend-mode: multiply;">' if aleph_b64 else '<span style="font-weight:900; font-size:20px;">ALEPH</span>'
onomo_img_tag = f'<img src="data:image/jpeg;base64,{onomo_b64}" width="170" style="mix-blend-mode: multiply;">' if onomo_b64 else '<span style="font-weight:900; font-size:20px;">ONOMO</span>'

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0 30px 0; border-bottom: 1px solid rgba(0,0,0,0.05); margin-bottom: 40px;">
    <div style="flex: 1;">{aleph_img_tag}</div>
    <div style="flex: 2; text-align: center;">
        <h2 style
