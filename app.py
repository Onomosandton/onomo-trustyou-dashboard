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
                "cost": float(fields.get("cost", {}).get("doubleValue", fields.get("cost", {}).get("integerValue", 0))),
                "date": pd.to_datetime(fields.get("date", {}).get("stringValue", ""), errors='coerce'),
                "resolvedAt": pd.to_datetime(fields.get("resolvedAt", {}).get("stringValue", ""), errors='coerce')
            })
        return pd.DataFrame(records)
    except Exception:
        return pd.DataFrame()

fb_df = fetch_live_firebase_data()
if not fb_df.empty and 'date' in fb_df.columns:
    fb_df['date'] = pd.to_datetime(fb_df['date'], errors='coerce').dt.tz_localize(None)
    if 'resolvedAt' in fb_df.columns:
        fb_df['resolvedAt'] = pd.to_datetime(fb_df['resolvedAt'], errors='coerce').dt.tz_localize(None)
        fb_df['resolution_time_mins'] = (fb_df['resolvedAt'] - fb_df['date']).dt.total_seconds() / 60.0

# 5. Sidebar: GM Target Setup & File Upload
with st.sidebar:
    st.markdown("<h3 style='font-weight:900;'>⚙️ GM Target Setup</h3>", unsafe_allow_html=True)
    st.markdown("Set Year-End target scores per platform.")
    
    new_targets = {}
    for platform in ["TrustYou Survey", "booking.com", "google.com", "tripadvisor.com"]:
        new_targets[platform] = st.slider(f"{platform} Target", 50, 100, st.session_state.gm_targets.get(platform, 85))
    
    if st.button("Save Targets"):
        st.session_state.gm_targets = new_targets
        save_targets(new_targets)
        st.success("Targets locked.")
        
    st.markdown("---")
    uploaded_file = st.file_uploader("📂 Upload Weekly TrustYou Data", type=["csv"])
    if st.button("Reset Dashboard"):
        st.rerun()

# 6. Header
aleph_img_tag = f'<img src="data:image/png;base64,{aleph_b64}" width="160" style="mix-blend-mode: multiply;">' if aleph_b64 else '<span style="font-weight:900; font-size:20px;">ALEPH</span>'
onomo_img_tag = f'<img src="data:image/jpeg;base64,{onomo_b64}" width="170" style="mix-blend-mode: multiply;">' if onomo_b64 else '<span style="font-weight:900; font-size:20px;">ONOMO</span>'

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0 20px 0; border-bottom: 1px solid rgba(0,0,0,0.05); margin-bottom: 20px;">
    <div style="flex: 1;">{aleph_img_tag}</div>
    <div style="flex: 2; text-align: center;">
        <h2 style="margin: 0; color: #1A1A1A; font-weight: 900; letter-spacing: -0.5px; font-size: 2rem;">EXECUTIVE COMMAND CENTER</h2>
        <p style="margin: 5px 0 0 0; color: #7EC8BD; font-size: 0.95rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2.5px;">Sandton Predictive Operations</p>
    </div>
    <div style="flex: 1; display: flex; justify-content: flex-end;">{onomo_img_tag}</div>
</div>
""", unsafe_allow_html=True)

# 7. Core Application Logic
if uploaded_file is not None:
    try:
        ty_df = pd.read_csv(uploaded_file)
        ty_df['Score'] = pd.to_numeric(ty_df['Score'], errors='coerce')
        ty_df['Published date'] = pd.to_datetime(ty_df['Published date'], errors='coerce').dt.tz_localize(None)
        
        def mine_review_text_department(text):
            if pd.isna(text): return "General"
            txt = str(text).lower()
            if any(w in txt for w in ['breakfast', 'menu', 'salt', 'mogodu', 'food', 'chef', 'restaurant']): return "Food & Beverage"
            if any(w in txt for w in ['clean', 'dirty', 'housekeeping', 'sheets', 'stain', 'bed']): return "Housekeeping"
            if any(w in txt for w in ['aircon', 'ac', 'tv', 'internet', 'wifi', 'broken', 'maintenance', 'socket', 'latch']): return "Maintenance"
            if any(w in txt for w in ['front desk', 'reception', 'staff', 'polite', 'rude', 'friendly', 'check-in']): return "Front Desk"
            return "General"
            
        def cross_reference_synergy(row, live_db):
            detected_dept = mine_review_text_department(row.get('Review Text', ''))
            author_name = str(row['Author name']).lower().strip()
            review_date = row['Published date']
            
            if live_db.empty or pd.isna(review_date) or author_name in ['nan', '']:
                if detected_dept != "General": return "Resolved In-House" if row['Score'] >= 80 else "Slipped Through (Blindspot)"
                return "General Feedback"
            
            time_window = (live_db['date'] <= review_date) & (live_db['date'] >= (review_date - timedelta(days=7)))
            recent_logs = live_db[time_window]
            
            for _, fb_row in recent_logs.iterrows():
                logged_identifier = str(fb_row['guestName']).lower()
                if author_name in logged_identifier or logged_identifier in author_name:
                    if fb_row['type'] == 'compliment': return "Praise Confirmed"
                    return "Resolved In-House" if fb_row['status'] == 'resolved' else "Failed Escalation"
            
            return "Slipped Through (Blindspot)" if row['Score'] < 80 else "General Feedback"

        ty_df['Synergy_Metric'] = ty_df.apply(lambda r: cross_reference_synergy(r, fb_df), axis=1)
        ty_df['Extracted_Dept'] = ty_df['Review Text'].apply(mine_review_text_department)
        
        # --- SECTION 1: EXECUTIVE SUMMARY ---
        st.markdown("<div class='section-header'>1. Executive Summary</div>", unsafe_allow_html=True)
        
        total_reviews = len(ty_df)
        avg_score = ty_df['Score'].mean()
        
        # Calculate Target Achievement Pie Charts
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        pie_cols = st.columns(4)
        platforms = ["TrustYou Survey", "booking.com", "google.com", "tripadvisor.com"]
        
        for idx, platform in enumerate(platforms):
            target = st.session_state.gm_targets.get(platform, 85)
            plat_data = ty_df[ty_df['Source'].str.lower() == platform.lower()]
            actual = plat_data['Score'].mean() if not plat_data.empty else 0
            
            # Pie chart logic: If actual is 70 and target is 85, achieved = 70, missing = 15. 
            # If actual >= target, achieved = target, missing = 0.
            achieved = min(actual, target)
            missing = max(0, target - actual)
            
            fig = go.Figure(data=[go.Pie(
                labels=['Achieved', 'Gap to Target'],
                values=[achieved, missing] if actual > 0 else [0, 100],
                hole=.7,
                marker_colors=['#7EC8BD', '#F0F0F0'],
                textinfo='none'
            )])
            fig.update_layout(
                showlegend=False, height=180, margin=dict(t=0, b=0, l=0, r=0),
                annotations=[dict(text=f"{actual:.1f}%<br><span style='font-size:10px;color:#888'>Target: {target}</span>", x=0.5, y=0.5, font_size=16, showarrow=False)]
            )
            with pie_cols[idx]:
                st.markdown(f"<p style='text-align:center; font-weight:700; color:#1A1A1A; font-size:0.9rem;'>{platform}</p>", unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # --- SECTION 2: THE BRIDGE (SERVICE RECOVERY ROI) ---
        st.markdown("<div class='section-header'>2. The Service Recovery ROI</div>", unsafe_allow_html=True)
        
        saved_cases = ty_df[ty_df['Synergy_Metric'] == "Resolved In-House"]
        slipped_cases = ty_df[ty_df['Synergy_Metric'] == "Slipped Through (Blindspot)"]
        
        save_rate = (len(saved_cases) / (len(saved_cases) + len(slipped_cases))) * 100 if (len(saved_cases) + len(slipped_cases)) > 0 else 0
        revenue_at_risk_saved = len(saved_cases) * 2500  # Arbitrary ZAR 2500 ADR baseline for intercepted bad reviews
        
        c1, c2, c3 = st.columns(3, gap="medium")
        with c1: st.metric("The Save Rate", f"{save_rate:.1f}%", "Issues resolved yielding positive reviews")
        with c2: st.metric("Revenue at Risk Intercepted", f"R {revenue_at_risk_saved:,.2f}", "Saved via in-house resolution")
        with c3: st.metric("Slipped Through The Cracks", f"{len(slipped_cases)}", "Failed service recoveries", delta_color="inverse")
            
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        if not slipped_cases.empty:
            st.markdown("<h5 style='color: #8e2a2a; font-weight: 800; margin-bottom: 10px;'>Guests Who Slipped Through (Negative Post-Stay Reviews)</h5>", unsafe_allow_html=True)
            st.dataframe(slipped_cases[['Published date', 'Author name', 'Extracted_Dept', 'Score', 'Review Text']].sort_values('Score'), use_container_width=True, hide_index=True)
        else:
            st.success("No guests slipped through the cracks in this reporting period.")
        st.markdown("</div>", unsafe_allow_html=True)

        # --- SECTION 3: OPERATIONAL EFFICIENCY & LIVE STREAM ---
        st.markdown("<div class='section-header'>3. Operational Efficiency & Live Stream</div>", unsafe_allow_html=True)
        
        open_tickets = len(fb_df[fb_df['status'] == 'open']) if not fb_df.empty else 0
        avg_resp_time = fb_df['resolution_time_mins'].mean() if not fb_df.empty and 'resolution_time_mins' in fb_df.columns else 0
        
        e1, e2 = st.columns(2, gap="medium")
        with e1: st.metric("Live Open Tickets", f"{open_tickets}", "Currently tracked in-house", delta_color="inverse")
        with e2: st.metric("Average Resolution Time", f"{avg_resp_time:.1f} mins" if avg_resp_time > 0 else "N/A", "Target: <15 mins", delta_color="normal" if avg_resp_time <= 15 else "inverse")
        
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.markdown("<h5 style='color: #1A1A1A; font-weight: 800;'>Departmental Resolution Speed (Minutes)</h5>", unsafe_allow_html=True)
        if not fb_df.empty and 'resolution_time_mins' in fb_df.columns:
            dept_speed = fb_df.groupby('department')['resolution_time_mins'].mean().reset_index()
            fig_speed = px.bar(dept_speed, x='resolution_time_mins', y='department', orientation='h', color='department', color_discrete_sequence=["#1A1A1A", "#7EC8BD", "#A9B5B0", "#cf6231"])
            fig_speed.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False, xaxis_title="Average Minutes to Resolve", yaxis_title="")
            st.plotly_chart(fig_speed, use_container_width=True)
        else:
            st.info("Resolution timestamp data not fully available in current Firebase stream.")
        st.markdown("</div>", unsafe_allow_html=True)

        # --- SECTION 4: SENTIMENT & PREDICTIVE GAP ANALYSIS ---
        st.markdown("<div class='section-header'>4. Predictive Forecasting & Gap Analysis</div>", unsafe_allow_html=True)
        
        col_gap, col_heat = st.columns(2, gap="medium")
        
        with col_gap:
            st.markdown("<div class='glass-container' style='height: 100%;'>", unsafe_allow_html=True)
            st.markdown("<h5 style='color: #1A1A1A; font-weight: 800;'>The Feedback Gap</h5>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 0.85rem; color: #666;'>Comparing Live Issue Volume against Final TrustYou Scores.</p>", unsafe_allow_html=True)
            
            # Map Live Ticket Volume against TY Score per department
            if not fb_df.empty:
                live_vol = fb_df['department'].value_counts().reset_index()
                live_vol.columns = ['Department', 'Live_Tickets']
            else:
                live_vol = pd.DataFrame([{"Department": "Maintenance", "Live_Tickets": 5}, {"Department": "Housekeeping", "Live_Tickets": 2}])
                
            ty_dept_score = ty_df[ty_df['Extracted_Dept'] != 'General'].groupby('Extracted_Dept')['Score'].mean().reset_index()
            ty_dept_score.columns = ['Department', 'TY_Score']
            
            gap_df = pd.merge(live_vol, ty_dept_score, on='Department', how='outer').fillna(0)
            
            if not gap_df.empty:
                fig_gap = go.Figure()
                fig_gap.add_trace(go.Bar(x=gap_df['Department'], y=gap_df['Live_Tickets'], name='Live Tickets Logged', marker_color='#1A1A1A', yaxis='y1'))
                fig_gap.add_trace(go.Scatter(x=gap_df['Department'], y=gap_df['TY_Score'], name='TrustYou Score', marker_color='#cf6231', mode='lines+markers', yaxis='y2'))
                fig_gap.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    yaxis=dict(title="Live Tickets", side="left", showgrid=False),
                    yaxis2=dict(title="TrustYou Score", side="right", overlaying="y", range=[0, 100], showgrid=True, gridcolor='rgba(0,0,0,0.05)')
                )
                st.plotly_chart(fig_gap, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with col_heat:
            st.markdown("<div class='glass-container' style='height: 100%;'>", unsafe_allow_html=True)
            st.markdown("<h5 style='color: #1A1A1A; font-weight: 800;'>In-House Room Heatmap</h5>", unsafe_allow_html=True)
            st.markdown("<p style='font-size: 0.85rem; color: #666;'>Identifies specific rooms generating high complaint volumes live.</p>", unsafe_allow_html=True)
            
            if not fb_df.empty and 'guestName' in fb_df.columns:
                # Extract numeric room numbers from guestName field using regex
                fb_df['extracted_room'] = fb_df['guestName'].str.extract(r'(\d{3,4})')
                room_vol = fb_df.dropna(subset=['extracted_room'])['extracted_room'].value_counts().reset_index()
                room_vol.columns = ['Room Number', 'Incidents']
                
                if not room_vol.empty:
                    st.dataframe(room_vol.head(5), use_container_width=True, hide_index=True)
                    st.info("Note: Overlaying final TrustYou scores onto this heatmap requires Phase 2 PMS integration, as TrustYou exports omit room numbers.")
                else:
                    st.info("No valid room numbers found in recent in-house tracker entries.")
            else:
                st.info("Awaiting live data to generate floor heatmaps.")
            st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Pipeline Execution Failure: {e}")

else:
    st.markdown("<div class='glass-container' style='text-align: center; padding: 60px; color: #666;'><h4 style='font-weight:800; color:#1A1A1A; margin-bottom:10px;'>Awaiting Data Feed</h4><p>Upload your weekly TrustYou CSV via the sidebar to generate the Executive Summary.</p></div>", unsafe_allow_html=True)
