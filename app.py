import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
import base64
import os
import json
import xml.etree.ElementTree as ET
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
    
    div[data-testid="stFileUploader"] section { background-color: #FFFFFF !important; border: 2px dashed #7EC8BD !important; border-radius: 12px !important; padding: 15px !important; }
    div[data-testid="metric-container"] { background: #FFFFFF !important; padding: 20px; border-radius: 12px; border-top: 4px solid #7EC8BD; box-shadow: 0 10px 30px rgba(0,0,0,0.02); border: 1px solid rgba(0,0,0,0.01); }
    div[data-testid="metric-container"] label { color: #888888 !important; font-weight: 700 !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 1px; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #1A1A1A !important; font-weight: 900 !important; font-size: 2.2rem !important; }
    .glass-container { background: #FFFFFF !important; border-radius: 16px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.02); border: 1px solid rgba(0,0,0,0.01) !important; margin-bottom: 25px; }
    .section-header { font-size: 1.4rem; font-weight: 900; color: #1A1A1A; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 2px solid #F0F0F0; padding-bottom: 10px;}
</style>
""", unsafe_allow_html=True)

# 4. Data Extraction Pipelines (Firebase & Opera XML)
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
                "department": fields.get("department", {}).get("stringValue", "General"),
                "status": fields.get("status", {}).get("stringValue", "resolved"),
                "type": fields.get("type", {}).get("stringValue", "complaint"),
                "date": pd.to_datetime(fields.get("date", {}).get("stringValue", ""), errors='coerce'),
                "resolvedAt": pd.to_datetime(fields.get("resolvedAt", {}).get("stringValue", ""), errors='coerce')
            })
        return pd.DataFrame(records)
    except Exception:
        return pd.DataFrame()

def parse_opera_xml(xml_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        records = []
        for elem in root.findall('.//G_GROUP_BY1'):
            full_name = elem.find('FULL_NAME')
            room_no = elem.find('ROOM_NO')
            departure = elem.find('DEPARTURE')
            
            if full_name is not None and room_no is not None and departure is not None:
                # Clean Opera format: "Corcoles,Maria,MRS" -> "Maria Corcoles"
                name_parts = full_name.text.replace('*', '').split(',')
                clean_name = f"{name_parts[1]} {name_parts[0]}" if len(name_parts) >= 2 else name_parts[0]
                
                records.append({
                    "Opera_Name": clean_name.strip().lower(),
                    "Room_No": room_no.text.strip(),
                    "Departure": pd.to_datetime(departure.text.strip(), format="%d/%m/%y", errors='coerce')
                })
        return pd.DataFrame(records)
    except Exception as e:
        st.sidebar.error(f"XML Parsing Error: {e}")
        return pd.DataFrame()

# Fetch Live Firebase Feed
fb_df = fetch_live_firebase_data()
if not fb_df.empty and 'date' in fb_df.columns:
    fb_df['date'] = pd.to_datetime(fb_df['date'], errors='coerce').dt.tz_localize(None)
    if 'resolvedAt' in fb_df.columns:
        fb_df['resolvedAt'] = pd.to_datetime(fb_df['resolvedAt'], errors='coerce').dt.tz_localize(None)
        fb_df['resolution_time_mins'] = (fb_df['resolvedAt'] - fb_df['date']).dt.total_seconds() / 60.0

# 5. Sidebar: Target Setup & Dual File Upload
with st.sidebar:
    st.markdown("<h3 style='font-weight:900;'>⚙️ GM Target Setup</h3>", unsafe_allow_html=True)
    new_targets = {}
    for platform in ["TrustYou Survey", "booking.com", "google.com", "tripadvisor.com"]:
        new_targets[platform] = st.slider(f"{platform} Target", 50, 100, st.session_state.gm_targets.get(platform, 85))
    if st.button("Save Targets"):
        st.session_state.gm_targets = new_targets
        save_targets(new_targets)
        st.success("Targets locked.")
        
    st.markdown("---")
    st.markdown("<h4 style='font-weight:900;'>Data Ingestion</h4>", unsafe_allow_html=True)
    uploaded_csv = st.file_uploader("1. Drop Weekly TrustYou Data (.csv)", type=["csv"])
    uploaded_xml = st.file_uploader("2. Drop Opera PMS Report (.xml)", type=["xml"], help="Optional: Unlocks Room Heatmaps")
    if st.button("Reset Dashboard"): st.rerun()

# 6. Header
aleph_img_tag = '<img src="data:image/png;base64,' + aleph_b64 + '" width="160" style="mix-blend-mode: multiply;">' if aleph_b64 else '<span style="font-weight:900; font-size:20px;">ALEPH</span>'
onomo_img_tag = '<img src="data:image/jpeg;base64,' + onomo_b64 + '" width="170" style="mix-blend-mode: multiply;">' if onomo_b64 else '<span style="font-weight:900; font-size:20px;">ONOMO</span>'

header_html = """
<div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0 20px 0; border-bottom: 1px solid rgba(0,0,0,0.05); margin-bottom: 20px;">
    <div style="flex: 1;">""" + aleph_img_tag + """</div>
    <div style="flex: 2; text-align: center;">
        <h2 style="margin: 0; color: #1A1A1A; font-weight: 900; letter-spacing: -0.5px; font-size: 2rem;">EXECUTIVE COMMAND CENTER</h2>
        <p style="margin: 5px 0 0 0; color: #7EC8BD; font-size: 0.95rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2.5px;">Sandton Predictive Operations</p>
    </div>
    <div style="flex: 1; display: flex; justify-content: flex-end;">""" + onomo_img_tag + """</div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# 7. Core Application Logic
if uploaded_csv is not None:
    try:
        # Load TrustYou
        ty_df = pd.read_csv(uploaded_csv)
        ty_df['Score'] = pd.to_numeric(ty_df['Score'], errors='coerce')
        ty_df['Published date'] = pd.to_datetime(ty_df['Published date'], errors='coerce').dt.tz_localize(None)
        
        # Load Opera PMS XML if provided
        opera_df = pd.DataFrame()
        if uploaded_xml is not None:
            opera_df = parse_opera_xml(uploaded_xml)
        
        def mine_review_text_department(text):
            if pd.isna(text): return "General"
            txt = str(text).lower()
            if any(w in txt for w in ['breakfast', 'menu', 'salt', 'mogodu', 'food', 'chef', 'restaurant']): return "Food & Beverage"
            if any(w in txt for w in ['clean', 'dirty', 'housekeeping', 'sheets', 'stain', 'bed']): return "Housekeeping"
            if any(w in txt for w in ['aircon', 'ac', 'tv', 'internet', 'wifi', 'broken', 'maintenance', 'socket', 'latch']): return "Maintenance"
            if any(w in txt for w in ['front desk', 'reception', 'staff', 'polite', 'rude', 'friendly', 'check-in']): return "Front Desk"
            return "General"
            
        def extract_opera_room(ty_row, op_db):
            if op_db.empty: return None
            author = str(ty_row['Author name']).lower().strip()
            if author == 'nan' or author == '': return None
            
            # Fuzzy match TrustYou Author Name to Opera PMS Name within 10 days of review
            mask = (op_db['Departure'] >= ty_row['Published date'] - timedelta(days=10)) & (op_db['Departure'] <= ty_row['Published date'] + timedelta(days=3))
            recent_guests = op_db[mask]
            
            for _, op_row in recent_guests.iterrows():
                # Checking if TrustYou first name (e.g., 'Maria') is in Opera Name (e.g., 'Maria Corcoles')
                if author in op_row['Opera_Name'] or op_row['Opera_Name'] in author:
                    return op_row['Room_No']
            return None

        def cross_reference_synergy(row, live_db):
            detected_dept = mine_review_text_department(row.get('Review Text', ''))
            author_name = str(row['Author name']).lower().strip()
            review_date = row['Published date']
            
            if live_db.empty or pd.isna(review_date) or author_name in ['nan', '']:
                if detected_dept != "General": 
                    return "Resolved In-House" if row['Score'] >= 80 else "Slipped Through (Blindspot)"
                return "General Feedback"
            
            time_window = (live_db['date'] <= review_date) & (live_db['date'] >= (review_date - timedelta(days=7)))
            for _, fb_row in live_db[time_window].iterrows():
                if author_name in str(fb_row['guestName']).lower():
                    if fb_row['type'] == 'compliment': return "Praise Confirmed"
                    return "Resolved In-House" if fb_row['status'] == 'resolved' else "Failed Escalation"
            
            return "Slipped Through (Blindspot)" if row['Score'] < 80 else "General Feedback"

        # Apply Triangulation
        ty_df['Extracted_Dept'] = ty_df['Review Text'].apply(mine_review_text_department)
        ty_df['Synergy_Metric'] = ty_df.apply(lambda r: cross_reference_synergy(r, fb_df), axis=1)
        ty_df['Opera_Room'] = ty_df.apply(lambda r: extract_opera_room(r, opera_df), axis=1)
        
        # --- SECTION 1: EXECUTIVE SUMMARY ---
        st.markdown("<div class='section-header'>1. Executive Summary</div>", unsafe_allow_html=True)
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        pie_cols = st.columns(4)
        platforms = ["TrustYou Survey", "booking.com", "google.com", "tripadvisor.com"]
        
        for idx, platform in enumerate(platforms):
            target = st.session_state.gm_targets.get(platform, 85)
            plat_data = ty_df[ty_df['Source'].str.lower() == platform.lower()]
            actual = plat_data['Score'].mean() if not plat_data.empty else 0
            
            achieved, missing = min(actual, target), max(0, target - actual)
            fig = go.Figure(data=[go.Pie(labels=['Achieved', 'Gap to Target'], values=[achieved, missing] if actual > 0 else [0, 100], hole=.7, marker_colors=['#7EC8BD', '#F0F0F0'], textinfo='none')])
            fig.update_layout(showlegend=False, height=180, margin=dict(t=0, b=0, l=0, r=0), annotations=[dict(text=f"{actual:.1f}%<br><span style='font-size:10px;color:#888'>Target: {target}</span>", x=0.5, y=0.5, font_size=16, showarrow=False)])
            with pie_cols[idx]:
                st.markdown(f"<p style='text-align:center; font-weight:700; color:#1A1A1A; font-size:0.9rem;'>{platform}</p>", unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # --- SECTION 2: THE BRIDGE (SERVICE RECOVERY ROI) ---
        st.markdown("<div class='section-header'>2. The Service Recovery ROI</div>", unsafe_allow_html=True)
        saved_cases = ty_df[ty_df['Synergy_Metric'] == "Resolved In-House"]
        slipped_cases = ty_df[ty_df['Synergy_Metric'] == "Slipped Through (Blindspot)"]
        save_rate = (len(saved_cases) / (len(saved_cases) + len(slipped_cases))) * 100 if (len(saved_cases) + len(slipped_cases)) > 0 else 0
        
        c1, c2, c3 = st.columns(3, gap="medium")
        with c1: st.metric("The Save Rate", f"{save_rate:.1f}%", "Issues resolved yielding positive reviews")
        with c2: st.metric("Revenue at Risk Intercepted", f"R {len(saved_cases) * 2500:,.2f}", "Saved via in-house resolution")
        with c3: st.metric("Slipped Through The Cracks", f"{len(slipped_cases)}", "Failed service recoveries", delta_color="inverse")

        # --- SECTION 3: UNIFIED ROOM BURN-RATE HEATMAP ---
        st.markdown("<div class='section-header'>3. Unified Floor Heatmap (All Platforms)</div>", unsafe_allow_html=True)
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        
        # Build the unified heat matrix
        heatmap_data = []
        
        # Add Live Vercel Tickets
        if not fb_df.empty and 'guestName' in fb_df.columns:
            fb_df['Room'] = fb_df['guestName'].str.extract(r'(\d{3,4})')
            for _, row in fb_df.dropna(subset=['Room']).iterrows():
                heatmap_data.append({"Room": row['Room'], "Department": row['department'], "Source": "Live Tracker", "Weight": 1})
                
        # Add TrustYou Negative Reviews (Triangulated via Opera)
        if not ty_df.empty:
            mapped_ty = ty_df[ty_df['Opera_Room'].notna() & (ty_df['Score'] < 80)]
            for _, row in mapped_ty.iterrows():
                heatmap_data.append({"Room": str(row['Opera_Room']), "Department": row['Extracted_Dept'], "Source": "TrustYou (Negative)", "Weight": 2}) # Bad reviews weigh heavier
                
        heat_df = pd.DataFrame(heatmap_data)
        
        if not heat_df.empty:
            heat_df['Floor'] = "Floor " + heat_df['Room'].str[:-2]
            floor_vol = heat_df.groupby(['Floor', 'Room', 'Source']).sum('Weight').reset_index()
            
            fig_heat = px.treemap(
                floor_vol, path=['Floor', 'Room', 'Source'], values='Weight', color='Source',
                color_discrete_map={"Live Tracker": "#cf6231", "TrustYou (Negative)": "#8e2a2a"}
            )
            fig_heat.update_layout(margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", height=400)
            st.plotly_chart(fig_heat, use_container_width=True)
            st.info("💡 **How to read:** Orange blocks represent live Vercel maintenance/housekeeping tickets. Red blocks represent bad TrustYou reviews mapped directly to the room via the Opera PMS file. Double-layered rooms require immediate CapEx or HOD intervention.")
        else:
            if uploaded_xml is None:
                st.warning("Upload the Opera PMS XML file to unlock physical Room-Level TrustYou mapping.")
            else:
                st.info("No negative room-specific issues detected across platforms.")
        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Pipeline Execution Failure: {e}")

else:
    st.markdown("<div class='glass-container' style='text-align: center; padding: 60px; color: #666;'><h4 style='font-weight:800; color:#1A1A1A; margin-bottom:10px;'>Awaiting Data Feed</h4><p>Upload your weekly TrustYou CSV via the sidebar to generate the Executive Summary.</p></div>", unsafe_allow_html=True)
