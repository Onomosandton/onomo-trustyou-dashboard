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
st.set_page_config(page_title="Insights Dashboard", layout="wide", initial_sidebar_state="collapsed")

# 2. State Management for Uploads & Targets
if 'active_report' not in st.session_state:
    st.session_state.active_report = False
if 'ty_df' not in st.session_state:
    st.session_state.ty_df = pd.DataFrame()
if 'opera_df' not in st.session_state:
    st.session_state.opera_df = pd.DataFrame()
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0

TARGETS_FILE = "gm_targets.json"

def load_targets():
    if os.path.exists(TARGETS_FILE):
        with open(TARGETS_FILE, "r") as f:
            return json.load(f)
    return {
        "TrustYou Survey": 85, "booking.com": 85, "google.com": 85, "tripadvisor.com": 85,
        "ADR": 1500, "Room Revenue": 500000, "F&B Revenue": 150000
    }

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
    [data-testid="stHeader"] { background-color: transparent !important; }
    [data-testid="stToolbar"] { display: none !important; }
    footer { display: none !important; }
    
    .stApp { background-color: #F8F9FA; }
    h1, h2, h3, h4, h5, h6, p, span, div { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    
    div[data-testid="stFileUploader"] section { background-color: #FFFFFF !important; border: 2px dashed #7EC8BD !important; border-radius: 12px !important; padding: 15px !important; }
    div[data-testid="metric-container"] { background: #FFFFFF !important; padding: 15px; border-radius: 12px; border-top: 4px solid #7EC8BD; box-shadow: 0 10px 30px rgba(0,0,0,0.02); border: 1px solid rgba(0,0,0,0.01); }
    div[data-testid="metric-container"] label { color: #888888 !important; font-weight: 700 !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 1px; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #1A1A1A !important; font-weight: 900 !important; font-size: 2rem !important; }
    .glass-container { background: #FFFFFF !important; border-radius: 16px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); border: 1px solid rgba(0,0,0,0.02) !important; margin-bottom: 25px; }
    
    .alert-box { background: #FFF4F4; border-left: 4px solid #8e2a2a; padding: 10px 15px; border-radius: 4px; margin-bottom: 8px; font-size: 0.9rem; color: #8e2a2a; font-weight: 700; }
    .stable-box { background: #F0F9F8; border-left: 4px solid #7EC8BD; padding: 10px 15px; border-radius: 4px; margin-bottom: 8px; font-size: 0.9rem; color: #4A5D54; font-weight: 700; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { font-weight: 800; font-size: 1.1rem; padding-top: 15px; padding-bottom: 15px; color: #666; }
    .stTabs [aria-selected="true"] { color: #1A1A1A !important; border-bottom: 3px solid #7EC8BD !important; }
    
    .streamlit-expanderHeader { color: #333 !important; font-size: 0.95rem !important; font-weight: 800 !important; }
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
    except Exception:
        return pd.DataFrame()

fb_df = fetch_live_firebase_data()
open_tickets_total = 0
open_tickets_24h = 0
criticals = pd.Series(dtype=int)

if not fb_df.empty and 'date' in fb_df.columns:
    fb_df['date'] = pd.to_datetime(fb_df['date'], errors='coerce').dt.tz_localize(None)
    if 'resolvedAt' in fb_df.columns:
        fb_df['resolvedAt'] = pd.to_datetime(fb_df['resolvedAt'], errors='coerce').dt.tz_localize(None)
        fb_df['resolution_time_mins'] = (fb_df['resolvedAt'] - fb_df['date']).dt.total_seconds() / 60.0
    
    open_tickets_total = len(fb_df[fb_df['status'] == 'open'])
    last_24h_boundary = pd.Timestamp.now().replace(tzinfo=None) - pd.Timedelta(days=1)
    open_tickets_24h = len(fb_df[(fb_df['status'] == 'open') & (fb_df['date'] >= last_24h_boundary)])
    
    if 'guestName' in fb_df.columns:
        rooms = fb_df['guestName'].str.extract(r'(\d{3,4})')[0].dropna()
        if not rooms.empty:
            counts = rooms.value_counts()
            criticals = counts[counts >= 2]

# 5. Header Component
aleph_img_tag = '<img src="data:image/png;base64,' + aleph_b64 + '" width="160" style="mix-blend-mode: multiply;">' if aleph_b64 else '<span style="font-weight:900; font-size:20px;">ALEPH</span>'
onomo_img_tag = '<img src="data:image/jpeg;base64,' + onomo_b64 + '" width="170" style="mix-blend-mode: multiply;">' if onomo_b64 else '<span style="font-weight:900; font-size:20px;">ONOMO</span>'

header_html = """
<div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0 20px 0; border-bottom: 1px solid rgba(0,0,0,0.05); margin-bottom: 30px;">
    <div style="flex: 1;">""" + aleph_img_tag + """</div>
    <div style="flex: 2; text-align: center;">
        <h2 style="margin: 0; color: #1A1A1A; font-weight: 900; letter-spacing: -0.5px; font-size: 2rem;">INSIGHTS DASHBOARD</h2>
        <p style="margin: 5px 0 0 0; color: #7EC8BD; font-size: 0.95rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2.5px;">Sandton Predictive Operations</p>
    </div>
    <div style="flex: 1; display: flex; justify-content: flex-end;">""" + onomo_img_tag + """</div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# 6. Central Application Logic
if not st.session_state.active_report:
    # --- WELCOME LANDING PAGE ---
    welcome_left, welcome_right = st.columns([1.1, 1], gap="large")
    
    with welcome_left:
        
        tracker_state = "Online" if not fb_df.empty else "Offline"
        st.markdown(f"""
        <div style='margin-bottom: 25px;'>
            <h2 style='color: #1A1A1A; font-weight: 900; font-size: 1.8rem; margin-bottom: 25px;'>Live Floor Snapshot</h2>
            <div style='display: flex; justify-content: space-between; padding-bottom: 5px; width: 85%;'>
                <div>
                    <div style='color: #666; font-size: 0.85rem; margin-bottom: 5px;'>Tracker Status</div>
                    <div style='color: #2C3E50; font-size: 2.2rem; font-weight: 400; line-height: 1;'>{tracker_state}</div>
                </div>
                <div>
                    <div style='color: #666; font-size: 0.85rem; margin-bottom: 5px;'>Active Last 24 Hrs</div>
                    <div style='color: #2C3E50; font-size: 2.2rem; font-weight: 400; line-height: 1;'>{open_tickets_24h}</div>
                </div>
                <div>
                    <div style='color: #666; font-size: 0.85rem; margin-bottom: 5px;'>Total Cycle Backlog</div>
                    <div style='color: #2C3E50; font-size: 2.2rem; font-weight: 400; line-height: 1;'>{open_tickets_total}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        with st.expander("View Active Backlog Details", expanded=False):
            if not fb_df.empty:
                active_df = fb_df[fb_df['status'] == 'open'][['date', 'guestName', 'department', 'type']].sort_values('date', ascending=False)
                if not active_df.empty:
                    st.dataframe(active_df, hide_index=True, use_container_width=True)
                else:
                    st.success("[STATUS NORMAL] No open tickets currently backlogged.")
            else:
                st.info("System Offline: Awaiting live tracker data.")
                
        with st.expander(f"View Critical Room Alerts ({len(criticals)})", expanded=False):
            if not criticals.empty:
                for rm, ct in criticals.items():
                    st.markdown(f"<p style='color:#8e2a2a; font-weight:600; font-size: 0.9rem; margin:0; padding: 5px 0;'>[ALERT] Room {rm}: {ct} unresolved complaints recorded.</p>", unsafe_allow_html=True)
            else:
                st.success("[STATUS NORMAL] Floor stable. No repeat critical issues detected.")
                
        with st.expander("Target Configurations", expanded=False):
            st.markdown("<p style='font-size: 0.85rem; color: #666; margin-bottom: 15px;'>Set baseline performance targets for year-end calculations.</p>", unsafe_allow_html=True)
            
            # --- SECTION 1: ONLINE REVIEW SCORES ---
            st.markdown("<div style='font-weight: 700; font-size: 0.85rem; color: #1A1A1A; margin-bottom: 10px; text-transform: uppercase;'>Section 1: Online Review Scores</div>", unsafe_allow_html=True)
            t_c1, t_c2 = st.columns(2)
            new_targets = {}
            with t_c1:
                new_targets["TrustYou Survey"] = st.slider("TrustYou Score", 50, 100, st.session_state.gm_targets.get("TrustYou Survey", 85))
                new_targets["google.com"] = st.slider("Google Score", 50, 100, st.session_state.gm_targets.get("google.com", 85))
            with t_c2:
                new_targets["booking.com"] = st.slider("Booking.com Score", 50, 100, st.session_state.gm_targets.get("booking.com", 85))
                new_targets["tripadvisor.com"] = st.slider("TripAdvisor Score", 50, 100, st.session_state.gm_targets.get("tripadvisor.com", 85))
            
            st.markdown("<hr style='margin: 15px 0px; border-color: rgba(0,0,0,0.05);'>", unsafe_allow_html=True)
            
            # --- SECTION 2: FINANCIALS ---
            st.markdown("<div style='font-weight: 700; font-size: 0.85rem; color: #1A1A1A; margin-bottom: 10px; text-transform: uppercase;'>Section 2: Financials</div>", unsafe_allow_html=True)
            f_c1, f_c2, f_c3 = st.columns(3)
            with f_c1:
                new_targets["ADR"] = st.number_input("ADR (ZAR)", value=st.session_state.gm_targets.get("ADR", 1500), step=50)
            with f_c2:
                new_targets["Room Revenue"] = st.number_input("Room Revenue (ZAR)", value=st.session_state.gm_targets.get("Room Revenue", 500000), step=10000)
            with f_c3:
                new_targets["F&B Revenue"] = st.number_input("F&B Revenue (ZAR)", value=st.session_state.gm_targets.get("F&B Revenue", 150000), step=5000)
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Save Targets", use_container_width=True):
                st.session_state.gm_targets = new_targets
                save_targets(new_targets)
                st.success("System configurations updated.")
                
        with st.expander("Data Synchronization", expanded=False):
            st.markdown("<p style='font-size: 0.85rem; color: #666; margin-bottom: 15px;'>Upload weekly reports to generate the Executive Summary.</p>", unsafe_allow_html=True)
            col_csv, col_xml = st.columns(2)
            with col_csv:
                csv_file = st.file_uploader("Upload TrustYou Data (.csv) [REQUIRED]", type=["csv"], key=f"csv_up_{st.session_state.uploader_key}")
            with col_xml:
                xml_file = st.file_uploader("Upload Opera PMS Report (.xml) [OPTIONAL]", type=["xml"], key=f"xml_up_{st.session_state.uploader_key}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Generate Analytics", use_container_width=True, type="primary"):
                if csv_file is not None:
                    parsed_ty = pd.read_csv(csv_file)
                    parsed_ty['Score'] = pd.to_numeric(parsed_ty['Score'], errors='coerce')
                    parsed_ty['Published date'] = pd.to_datetime(parsed_ty['Published date'], errors='coerce').dt.tz_localize(None)
                    st.session_state.ty_df = parsed_ty
                    
                    if xml_file is not None:
                        st.session_state.opera_df = parse_opera_xml(xml_file)
                    else:
                        st.session_state.opera_df = pd.DataFrame()
                        
                    st.session_state.active_report = True
                    st.rerun()
                else:
                    st.error("Please upload the required TrustYou CSV to proceed.")

    with welcome_right:
        img_src = "data:image/jpeg;base64," + vibe_b64 if vibe_b64 else "https://images.unsplash.com/photo-1542314831-c6a4d14d8c53?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
        image_html = f"""
        <div style="box-shadow: 0 20px 50px rgba(0,0,0,0.15); border-radius: 24px; overflow: hidden; margin-top: 10px;">
            <img src="{img_src}" style="width: 100%; display: block; object-fit: cover;">
        </div>"""
        st.markdown(image_html, unsafe_allow_html=True)

else:
    # --- ACTIVE ANALYTICS DASHBOARD ---
    col_back, col_space = st.columns([1, 5])
    with col_back:
        if st.button("Close Report / Return to Hub", use_container_width=True):
            st.session_state.active_report = False
            st.session_state.ty_df = pd.DataFrame()
            st.session_state.opera_df = pd.DataFrame()
            st.session_state.uploader_key += 1
            st.rerun()
            
    st.markdown("<hr style='margin: 10px 0px 20px 0px;'>", unsafe_allow_html=True)
    
    try:
        ty_df = st.session_state.ty_df
        opera_df = st.session_state.opera_df
        
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
                    if st.session_state.opera_df.empty: st.warning("Upload the Opera PMS XML file to unlock physical Room-Level TrustYou mapping.")
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
