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
st.set_page_config(page_title="Insights Dashboard", layout="wide", initial_sidebar_state="expanded")

# 2. State Management for Resetting & Targets
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

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
vibe_b64 = get_base64_image("vibe1.jpg")

st.markdown("""
<style>
    [data-testid="stToolbar"] {display: none !important;}
    footer {display: none !important;}
    header {display: none !important;}
    .stApp { background-color: #F8F9FA; }
    h1, h2, h3, h4, h5, h6, p, span, div { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    
    div[data-testid="stFileUploader"] section { background-color: #FFFFFF !important; border: 2px dashed #7EC8BD !important; border-radius: 12px !important; padding: 15px !important; }
    div[data-testid="metric-container"] { background: #FFFFFF !important; padding: 15px; border-radius: 12px; border-top: 4px solid #7EC8BD; box-shadow: 0 10px 30px rgba(0,0,0,0.02); border: 1px solid rgba(0,0,0,0.01); }
    div[data-testid="metric-container"] label { color: #888888 !important; font-weight: 700 !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 1px; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #1A1A1A !important; font-weight: 900 !important; font-size: 2rem !important; }
    .glass-container { background: #FFFFFF !important; border-radius: 16px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); border: 1px solid rgba(0,0,0,0.02) !important; margin-bottom: 25px; }
    .alert-box { background: #FFF4F4; border-left: 4px solid #8e2a2a; padding: 10px 15px; border-radius: 4px; margin-bottom: 8px; font-size: 0.9rem; color: #8e2a2a; font-weight: 700; }
    .stable-box { background: #F0F9F8; border-left: 4px solid #7EC8BD; padding: 10px 15px; border-radius: 4px; margin-bottom: 8px; font-size: 0.9rem; color: #4A5D54; font-weight: 700; }
    
    /* Style Streamlit Tabs for a cleaner dashboard feel */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { font-weight: 800; font-size: 1.1rem; padding-top: 15px; padding-bottom: 15px; color: #666; }
    .stTabs [aria-selected="true"] { color: #1A1A1A !important; border-bottom: 3px solid #7EC8BD !important; }
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
                "department": fields.get("department", {}).get("stringValue", "General"),
                "status": fields.get("status", {}).get("stringValue", "resolved"),
                "type": fields.get("type", {}).get("stringValue", "complaint"),
                "cost": float(fields.get("cost", {}).get("doubleValue", fields.get("cost", {}).get("integerValue", 0))),
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
                name_parts = full_name.text.replace('*', '').split(',')
                clean_name = f"{name_parts[1]} {name_parts[0]}" if len(name_parts) >= 2 else name_parts[0]
                
                records.append({
                    "Opera_Name": clean_name.strip().lower(),
                    "Room_No": room_no.text.strip(),
                    "Departure": pd.to_datetime(departure.text.strip(), format="%d/%m/%y", errors='coerce')
                })
        return pd.DataFrame(records)
    except Exception as e:
        st.error(f"XML Parsing Error: {e}")
        return pd.DataFrame()

fb_df = fetch_live_firebase_data()
open_tickets_total = 0
open_tickets_24h = 0
alerts_html = ""

if not fb_df.empty and 'date' in fb_df.columns:
    fb_df['date'] = pd.to_datetime(fb_df['date'], errors='coerce').dt.tz_localize(None)
    if 'resolvedAt' in fb_df.columns:
        fb_df['resolvedAt'] = pd.to_datetime(fb_df['resolvedAt'], errors='coerce').dt.tz_localize(None)
        fb_df['resolution_time_mins'] = (fb_df['resolvedAt'] - fb_df['date']).dt.total_seconds() / 60.0
    
    open_tickets_total = len(fb_df[fb_df['status'] == 'open'])
    
    # Calculate Last 24 Hours
    last_24h_boundary = pd.Timestamp.now().replace(tzinfo=None) - pd.Timedelta(days=1)
    open_tickets_24h = len(fb_df[(fb_df['status'] == 'open') & (fb_df['date'] >= last_24h_boundary)])
    
    if 'guestName' in fb_df.columns:
        rooms = fb_df['guestName'].str.extract(r'(\d{3,4})')[0].dropna()
        if not rooms.empty:
            counts = rooms.value_counts()
            criticals = counts[counts >= 2]
            
            # Limit to Top 3 to prevent scrolling fatigue
            for rm, ct in criticals.head(3).items():
                alerts_html += f"<div class='alert-box'>Alert: Room {rm} - {ct} unresolved complaints recorded.</div>"
            
            if len(criticals) > 3:
                alerts_html += f"<div style='font-size: 0.85rem; color: #888; font-weight: 700; margin-top: 5px;'>+ {len(criticals) - 3} additional rooms require attention.</div>"

if alerts_html == "":
    alerts_html = "<div class='stable-box'>Status Normal: No repeat critical issues detected.</div>"

# 5. Sidebar Restored (Targets and Uploads)
with st.sidebar:
    st.markdown("<h3 style='font-weight:900;'>GM Target Setup</h3>", unsafe_allow_html=True)
    new_targets = {}
    for platform in ["TrustYou Survey", "booking.com", "google.com", "tripadvisor.com"]:
        new_targets[platform] = st.slider(f"{platform} Target", 50, 100, st.session_state.gm_targets.get(platform, 85))
    if st.button("Save Targets"):
        st.session_state.gm_targets = new_targets
        save_targets(new_targets)
        st.toast("Targets successfully locked.")
        
    st.markdown("---")
    st.markdown("<h3 style='font-weight:900;'>Data Ingestion</h3>", unsafe_allow_html=True)
    uploaded_csv = st.file_uploader("TrustYou Data (.csv)", type=["csv"], key=f"csv_up_{st.session_state.uploader_key}", help="Mandatory: Core sentiment scores.")
    uploaded_xml = st.file_uploader("Opera PMS Report (.xml)", type=["xml"], key=f"xml_up_{st.session_state.uploader_key}", help="Optional: Unlocks Room Heatmaps.")
    
    if uploaded_csv is not None:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Return to Hub", use_container_width=True):
            st.session_state.uploader_key += 1
            st.rerun()

# 6. Header Component
aleph_img_tag = '<img src="data:image/png;base64,' + aleph_b64 + '" width="160" style="mix-blend-mode: multiply;">' if aleph_b64 else '<span style="font-weight:900; font-size:20px;">ALEPH</span>'
onomo_img_tag = '<img src="data:image/jpeg;base64,' + onomo_b64 + '" width="170" style="mix-blend-mode: multiply;">' if onomo_b64 else '<span style="font-weight:900; font-size:20px;">ONOMO</span>'

header_html = """
<div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0 20px 0; border-bottom: 1px solid rgba(0,0,0,0.05); margin-bottom: 20px;">
    <div style="flex: 1;">""" + aleph_img_tag + """</div>
    <div style="flex: 2; text-align: center;">
        <h2 style="margin: 0; color: #1A1A1A; font-weight: 900; letter-spacing: -0.5px; font-size: 2rem;">INSIGHTS DASHBOARD</h2>
        <p style="margin: 5px 0 0 0; color: #7EC8BD; font-size: 0.95rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2.5px;">Sandton Predictive Operations</p>
    </div>
    <div style="flex: 1; display: flex; justify-content: flex-end;">""" + onomo_img_tag + """</div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# 7. Core Application Logic or Welcome Screen
if uploaded_csv is None:
    # --- RESTORED WELCOME DASHBOARD PAGE ---
    welcome_left, welcome_right = st.columns([1.1, 1], gap="large")
    
    with welcome_left:
        st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
        st.markdown("<h1 style='color: #1A1A1A; font-weight: 900; font-size: 3.5rem; line-height: 1.1; letter-spacing: -1.5px; margin-bottom: 20px;'>Sandton Predictive<br>Operations Hub.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #666666; font-size: 1.20rem; line-height: 1.7; margin-bottom: 40px; max-width: 95%;'>Sync live floor trackers with property management data to instantly identify service gaps, allocate maintenance workflows, and actively protect guest satisfaction scores. Please process your weekly exports via the sidebar.</p>", unsafe_allow_html=True)
        
        # Optimized Live Snapshot Grid
        tracker_state = "System Online" if not fb_df.empty else "System Offline"
        st.markdown(f"""
        <div class='glass-container'>
            <h4 style='margin-top:0; color: #1A1A1A; font-weight: 900;'>Live Floor Snapshot</h4>
            <div style='display: flex; justify-content: space-between; margin-top: 15px; padding-bottom: 15px; border-bottom: 1px solid rgba(0,0,0,0.05);'>
                <div>
                    <span style='color: #888; font-size: 0.75rem; text-transform: uppercase; font-weight: 800; letter-spacing: 1px;'>Tracker Status</span><br>
                    <span style='font-size: 1.6rem; font-weight: 900; color: #1A1A1A;'>{tracker_state}</span>
                </div>
                <div style='text-align: center;'>
                    <span style='color: #888; font-size: 0.75rem; text-transform: uppercase; font-weight: 800; letter-spacing: 1px;'>Active Last 24 Hrs</span><br>
                    <span style='font-size: 1.6rem; font-weight: 900; color: #cf6231;'>{open_tickets_24h}</span>
                </div>
                <div style='text-align: right;'>
                    <span style='color: #888; font-size: 0.75rem; text-transform: uppercase; font-weight: 800; letter-spacing: 1px;'>Total Cycle Backlog</span><br>
                    <span style='font-size: 1.6rem; font-weight: 900; color: #8e2a2a;'>{open_tickets_total}</span>
                </div>
            </div>
            <div style='margin-top: 15px;'>
                <span style='color: #888; font-size: 0.75rem; text-transform: uppercase; font-weight: 800; letter-spacing: 1px;'>Critical Active Alerts (Top 3 Offenders)</span><br>
                <div style='margin-top: 8px;'>{alerts_html}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
            
    with welcome_right:
        img_src = "data:image/jpeg;base64," + vibe_b64 if vibe_b64 else "https://images.unsplash.com/photo-1542314831-c6a4d14d8c53?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
        image_html = """
        <div style="box-shadow: 0 20px 50px rgba(0,0,0,0.15); border-radius: 24px; overflow: hidden; margin-top: 10px;">
            <img src=\"""" + img_src + """\" style="width: 100%; display: block; object-fit: cover;">
        </div>"""
        st.markdown(image_html, unsafe_allow_html=True)

else:
    # --- ACTIVE ANALYTICS DASHBOARD (BIRDSEYE TABS) ---
    try:
        ty_df = pd.read_csv(uploaded_csv)
        ty_df['Score'] = pd.to_numeric(ty_df['Score'], errors='coerce')
        ty_df['Published date'] = pd.to_datetime(ty_df['Published date'], errors='coerce').dt.tz_localize(None)
        
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
            mask = (op_db['Departure'] >= ty_row['Published date'] - timedelta(days=10)) & (op_db['Departure'] <= ty_row['Published date'] + timedelta(days=3))
            for _, op_row in op_db[mask].iterrows():
                if author in op_row['Opera_Name'] or op_row['Opera_Name'] in author: return op_row['Room_No']
            return None

        def cross_reference_synergy(row, live_db):
            detected_dept = mine_review_text_department(row.get('Review Text', ''))
            author_name = str(row['Author name']).lower().strip()
            review_date = row['Published date']
            
            if live_db.empty or pd.isna(review_date) or author_name in ['nan', '']:
                if detected_dept != "General": return ("Resolved In-House" if row['Score'] >= 80 else "Slipped Through (Blindspot)", 0.0)
                return ("General Feedback", 0.0)
            
            time_window = (live_db['date'] <= review_date) & (live_db['date'] >= (review_date - timedelta(days=7)))
            for _, fb_row in live_db[time_window].iterrows():
                if author_name in str(fb_row['guestName']).lower():
                    actual_cost = float(fb_row.get('cost', 0.0))
                    if fb_row['type'] == 'compliment': return ("Praise Confirmed", 0.0)
                    return ("Resolved In-House" if fb_row['status'] == 'resolved' else "Failed Escalation", actual_cost)
            
            return ("Slipped Through (Blindspot)" if row['Score'] < 80 else "General Feedback", 0.0)

        # Apply Triangulation
        ty_df['Extracted_Dept'] = ty_df['Review Text'].apply(mine_review_text_department)
        synergy_results = ty_df.apply(lambda r: cross_reference_synergy(r, fb_df), axis=1)
        ty_df['Synergy_Metric'] = [res[0] for res in synergy_results]
        ty_df['Recovery_Cost'] = [res[1] for res in synergy_results]
        ty_df['Opera_Room'] = ty_df.apply(lambda r: extract_opera_room(r, opera_df), axis=1)
        
        total_reviews = len(ty_df)
        avg_score = ty_df['Score'].mean()
        actual_blindspots = len(ty_df[ty_df['Synergy_Metric'] == "Slipped Through (Blindspot)"])
        catch_rate = ((total_reviews - actual_blindspots) / total_reviews) * 100 if total_reviews > 0 else 0

        # === THE BIRDSEYE TABS ===
        tab1, tab2, tab3 = st.tabs(["Executive Summary", "Service Recovery & ROI", "Floor Operations & Heatmap"])

        with tab1:
            st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
            col1, col2, col3, col4 = st.columns(4, gap="medium")
            with col1: st.metric("Reviews Correlated", f"{total_reviews}")
            with col2: st.metric("Overall Score", f"{avg_score:.1f}%")
            with col3: st.metric("In-House Blindspots", f"{actual_blindspots}", "Missed opportunities", delta_color="inverse")
            with col4: st.metric("Operational Catch Rate", f"{catch_rate:.1f}%", "Synergy baseline targets")
            
            st.markdown("<div class='glass-container' style='margin-top: 20px;'>", unsafe_allow_html=True)
            st.markdown("<h5 style='color: #1A1A1A; font-weight: 800; margin-bottom: 15px;'>Platform Target Achievement</h5>", unsafe_allow_html=True)
            pie_cols = st.columns(4)
            platforms = ["TrustYou Survey", "booking.com", "google.com", "tripadvisor.com"]
            for idx, platform in enumerate(platforms):
                target = st.session_state.gm_targets.get(platform, 85)
                plat_data = ty_df[ty_df['Source'].str.lower() == platform.lower()]
                actual = plat_data['Score'].mean() if not plat_data.empty else 0
                achieved, missing = min(actual, target), max(0, target - actual)
                
                fig = go.Figure(data=[go.Pie(labels=['Achieved', 'Gap'], values=[achieved, missing] if actual > 0 else [0, 100], hole=.7, marker_colors=['#7EC8BD', '#F0F0F0'], textinfo='none')])
                fig.update_layout(showlegend=False, height=180, margin=dict(t=0, b=0, l=0, r=0), annotations=[dict(text=f"{actual:.1f}%<br><span style='font-size:10px;color:#888'>Target: {target}</span>", x=0.5, y=0.5, font_size=16, showarrow=False)])
                with pie_cols[idx]:
                    st.markdown(f"<p style='text-align:center; font-weight:700; color:#1A1A1A; font-size:0.9rem;'>{platform}</p>", unsafe_allow_html=True)
                    st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with tab2:
            st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
            saved_cases = ty_df[ty_df['Synergy_Metric'] == "Resolved In-House"]
            slipped_cases = ty_df[ty_df['Synergy_Metric'] == "Slipped Through (Blindspot)"]
            
            actual_recovery_spend = saved_cases['Recovery_Cost'].sum()
            confirmed_praises = len(ty_df[ty_df['Synergy_Metric'] == "Praise Confirmed"])
            save_rate = (len(saved_cases) / (len(saved_cases) + len(slipped_cases))) * 100 if (len(saved_cases) + len(slipped_cases)) > 0 else 0
            
            c1, c2, c3, c4 = st.columns(4, gap="medium")
            with c1: st.metric("The Save Rate", f"{save_rate:.1f}%", "Issues resolved yielding positive reviews")
            with c2: st.metric("Actual Recovery Cost", f"ZAR {actual_recovery_spend:,.2f}", "Live tracker resolution spend")
            with c3: st.metric("Confirmed Praises", f"{confirmed_praises}", "In-house praise matching positive review")
            with c4: st.metric("Failed Recoveries", f"{len(slipped_cases)}", "Slipped through to post-stay", delta_color="inverse")
            
            if not slipped_cases.empty:
                st.markdown("<div class='glass-container' style='margin-top: 20px;'>", unsafe_allow_html=True)
                st.markdown("<h5 style='color: #8e2a2a; font-weight: 800; margin-bottom: 10px;'>Drill-down: Guests Who Slipped Through (Negative Post-Stay Reviews)</h5>", unsafe_allow_html=True)
                st.dataframe(slipped_cases[['Published date', 'Author name', 'Extracted_Dept', 'Score', 'Review Text']].sort_values('Score'), use_container_width=True, hide_index=True)
                st.markdown("</div>", unsafe_allow_html=True)

        with tab3:
            st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
            
            heatmap_data = []
            if not fb_df.empty and 'guestName' in fb_df.columns:
                fb_df['Room'] = fb_df['guestName'].str.extract(r'(\d{3,4})')
                for _, row in fb_df.dropna(subset=['Room']).iterrows():
                    heatmap_data.append({"Room": row['Room'], "Department": row['department'], "Source": "Live Tracker", "Weight": 1})
                    
            if not ty_df.empty:
                mapped_ty = ty_df[ty_df['Opera_Room'].notna() & (ty_df['Score'] < 80)]
                for _, row in mapped_ty.iterrows():
                    heatmap_data.append({"Room": str(row['Opera_Room']), "Department": row['Extracted_Dept'], "Source": "TrustYou (Negative)", "Weight": 2})
                    
            heat_df = pd.DataFrame(heatmap_data)
            
            col_heat, col_grid = st.columns([1.2, 1], gap="large")
            
            with col_heat:
                st.markdown("<div class='glass-container' style='height: 100%;'>", unsafe_allow_html=True)
                st.markdown("<h5 style='color: #1A1A1A; font-weight: 800;'>Unified Floor Heatmap</h5>", unsafe_allow_html=True)
                st.info("Interaction Guide: Click a room or floor to zoom in. To zoom back out, click the top banner of the chart.")
                
                if not heat_df.empty:
                    heat_df['Floor'] = "Floor " + heat_df['Room'].str[:-2]
                    floor_vol = heat_df.groupby(['Floor', 'Room', 'Source'])['Weight'].sum().reset_index()
                    
                    fig_heat = px.treemap(
                        floor_vol, path=['Floor', 'Room', 'Source'], values='Weight', color='Source',
                        color_discrete_map={"Live Tracker": "#cf6231", "TrustYou (Negative)": "#8e2a2a"}
                    )
                    fig_heat.update_layout(margin=dict(t=25, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", height=350)
                    st.plotly_chart(fig_heat, use_container_width=True)
                else:
                    if uploaded_xml is None: st.warning("Upload the Opera PMS XML file to unlock physical Room-Level TrustYou mapping.")
                    else: st.success("No negative room-specific issues detected across platforms.")
                st.markdown("</div>", unsafe_allow_html=True)
                
            with col_grid:
                st.markdown("<div class='glass-container' style='height: 100%;'>", unsafe_allow_html=True)
                st.markdown("<h5 style='color: #1A1A1A; font-weight: 800;'>Room-Level Incident Log Interface</h5>", unsafe_allow_html=True)
                
                if not ty_df[ty_df['Opera_Room'].notna()].empty:
                    st.markdown("<p style='font-size: 0.85rem; color: #8e2a2a; font-weight: 700; margin-bottom: 5px;'>Post-Stay Discovered Issues (Via TrustYou)</p>", unsafe_allow_html=True)
                    drill_ty = ty_df[ty_df['Opera_Room'].notna() & (ty_df['Score'] < 80)][['Opera_Room', 'Extracted_Dept', 'Score']]
                    drill_ty.columns = ['Room', 'Complaint Dept', 'Score']
                    st.dataframe(drill_ty, hide_index=True, use_container_width=True, height=150)
                else:
                    st.markdown("<p style='font-size: 0.85rem; color: #888;'>No mapped post-stay issues.</p>", unsafe_allow_html=True)
                    
                st.markdown("<p style='font-size: 0.85rem; color: #cf6231; font-weight: 700; margin-bottom: 5px; margin-top: 15px;'>Live In-House Logged Issues (Via Tracker)</p>", unsafe_allow_html=True)
                if not fb_df.empty and 'Room' in fb_df.columns:
                    drill_fb = fb_df.dropna(subset=['Room'])[['Room', 'department', 'status']]
                    drill_fb.columns = ['Room', 'Logged Dept', 'Current Status']
                    st.dataframe(drill_fb, hide_index=True, use_container_width=True, height=150)
                else:
                    st.markdown("<p style='font-size: 0.85rem; color: #888;'>No live rooms actively mapped.</p>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Pipeline Execution Failure: {e}")
