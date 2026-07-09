import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import base64
import os
from datetime import datetime, timedelta

# 1. Page Configuration
st.set_page_config(page_title="Synergy Command Center", layout="wide", initial_sidebar_state="collapsed")

# 2. Automated Firebase Live Extraction Engine (HTTP Data Pipeline)
def fetch_live_firebase_data():
    try:
        # Pull configurations securely from Streamlit Secrets
        project_id = st.secrets["firebase"]["project_id"]
        
        # Target path matching the exact production collection configuration
        base_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents/artifacts/onomo_live_production_v1/public/data/feedback_entries"
        
        response = requests.get(base_url, params={"pageSize": 300}, timeout=10)
        if response.status_code != 200:
            return pd.DataFrame()
            
        data = response.json()
        documents = data.get("documents", [])
        
        records = []
        for doc in documents:
            fields = doc.get("fields", {})
            
            # Reconstruct the exact database schema fields
            guest_name = fields.get("guestName", {}).get("stringValue", "")
            department = fields.get("department", {}).get("stringValue", "")
            reason = fields.get("reason", {}).get("stringValue", "")
            status = fields.get("status", {}).get("stringValue", "resolved")
            entry_type = fields.get("type", {}).get("stringValue", "complaint")
            cost = fields.get("cost", {}).get("doubleValue", fields.get("cost", {}).get("integerValue", 0))
            date_str = fields.get("date", {}).get("stringValue", "")
            
            records.append({
                "guestName": str(guest_name).strip(),
                "department": department,
                "reason": reason,
                "status": status,
                "type": entry_type,
                "cost": float(cost),
                "date": pd.to_datetime(date_str, errors='coerce')
            })
            
        return pd.DataFrame(records)
    except Exception:
        return pd.DataFrame()

# 3. Asset Render Engine
def get_base64_image(filepath):
    if not os.path.exists(filepath): return None
    with open(filepath, "rb") as f: return base64.b64encode(f.read()).decode("utf-8")

aleph_b64 = get_base64_image("aleph_logo.png")
onomo_b64 = get_base64_image("onomo_logo.jpg")

# 4. Strict Branding CSS
st.markdown("""
<style>
    [data-testid="stToolbar"] {display: none !important;}
    footer {display: none !important;}
    header {display: none !important;}
    .stApp { background-color: #F8F9FA; }
    h1, h2, h3, h4, h5, h6, p, span, div { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; }
    
    div[data-testid="stFileUploader"] section {
        background-color: #FFFFFF !important; border: 2px dashed #7EC8BD !important; 
        border-radius: 12px !important; padding: 40px !important;
    }
    div[data-testid="metric-container"] {
        background: #FFFFFF !important; padding: 20px; border-radius: 12px;
        border-top: 4px solid #7EC8BD; box-shadow: 0 10px 30px rgba(0,0,0,0.03); border: 1px solid rgba(0,0,0,0.02);
    }
    div[data-testid="metric-container"] label { color: #888888 !important; font-weight: 700 !important; font-size: 0.80rem !important; text-transform: uppercase; letter-spacing: 1px; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #1A1A1A !important; font-weight: 900 !important; font-size: 2.2rem !important; }
    .glass-container { background: #FFFFFF !important; border-radius: 16px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.03); border: 1px solid rgba(0,0,0,0.02) !important; }
</style>
""", unsafe_allow_html=True)

# 5. Header Frame
aleph_img_tag = f'<img src="data:image/png;base64,{aleph_b64}" width="160" style="mix-blend-mode: multiply;">' if aleph_b64 else '<span style="font-weight:900; font-size:20px;">ALEPH</span>'
onomo_img_tag = f'<img src="data:image/jpeg;base64,{onomo_b64}" width="170" style="mix-blend-mode: multiply;">' if onomo_b64 else '<span style="font-weight:900; font-size:20px;">ONOMO</span>'

st.markdown(f"""
<div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0 30px 0; border-bottom: 1px solid rgba(0,0,0,0.05); margin-bottom: 40px;">
    <div style="flex: 1;">{aleph_img_tag}</div>
    <div style="flex: 2; text-align: center;">
        <h2 style="margin: 0; color: #1A1A1A; font-weight: 900; letter-spacing: -0.5px; font-size: 2rem;">SYNERGY COMMAND CENTER</h2>
        <p style="margin: 5px 0 0 0; color: #7EC8BD; font-size: 0.95rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2.5px;">Sandton Property Operations</p>
    </div>
    <div style="flex: 1; display: flex; justify-content: flex-end;">{onomo_img_tag}</div>
</div>
""", unsafe_allow_html=True)

if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

if st.session_state.uploaded_file is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #1A1A1A; font-weight: 900; font-size: 3rem;'>The Synergy Engine.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; font-size: 1.1rem; margin-bottom: 30px;'>Drop your weekly TrustYou review data file below. The application will auto-ping your database server to map in-house actions completely.</p>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Drop TrustYou CSV Here", type=["csv"], label_visibility="collapsed")
        if uploaded_file:
            st.session_state.uploaded_file = uploaded_file
            st.rerun()
else:
    if st.button("← Reset Dashboard"):
        st.session_state.uploaded_file = None
        st.rerun()
        
    try:
        # Load TrustYou data
        ty_df = pd.read_csv(st.session_state.uploaded_file)
        ty_df['Score'] = pd.to_numeric(ty_df['Score'], errors='coerce')
        ty_df['Published date'] = pd.to_datetime(ty_df['Published date'], errors='coerce')
        
        # Pull Live Operations database records completely over active REST pipeline
        fb_df = fetch_live_firebase_data()
        
        # 6. Cross-Platform Match Processing Core
        def map_live_operational_state(ty_row, live_db):
            if live_db.empty: return "Blindspot (Missed)" if ty_row['Score'] < 80 else "No Match Found"
            
            author_name = str(ty_row['Author name']).lower().strip()
            review_date = ty_row['Published date']
            
            if pd.isna(review_date) or author_name in ['nan', '']: return "No Match Found"
            
            # Limit cross-referencing to database tickets logged within a 7-day proximity window of checkout
            time_window = (live_db['date'] <= review_date) & (live_db['date'] >= (review_date - timedelta(days=7)))
            active_window_logs = live_db[time_window]
            
            for _, fb_row in active_window_logs.iterrows():
                logged_identifier = str(fb_row['guestName']).lower()
                
                # Check cross-reference string boundaries directly
                if author_name in logged_identifier or logged_identifier in author_name:
                    if fb_row['type'] == 'compliment': return "Praise Logged"
                    return "Issue Resolved In-House" if fb_row['status'] == 'resolved' else "Issue Logged - Unresolved"
            
            return "Blindspot (Missed)" if ty_row['Score'] < 80 else "No Match Found"

        # Apply automated matrix processing
        ty_df['Operational_Status'] = ty_df.apply(lambda r: map_live_operational_state(r, fb_df), axis=1)
        
        # 7. Generate Production Matrices
        total_reviews = len(ty_df)
        negative_reviews = ty_df[ty_df['Score'] < 80]
        blindspots = len(negative_reviews[negative_reviews['Operational_Status'] == "Blindspot (Missed)"])
        
        resolved_group = ty_df[ty_df['Operational_Status'] == "Issue Resolved In-House"]
        avg_score_resolved = resolved_group['Score'].mean() if not resolved_group.empty else 0
        
        unresolved_group = ty_df[ty_df['Operational_Status'] == "Issue Logged - Unresolved"]
        avg_score_failed = unresolved_group['Score'].mean() if not unresolved_group.empty else 0

        # Output Production KPIs
        st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4, gap="medium")
        with c1: st.metric("Reviews Checked", f"{total_reviews}")
        with c2: st.metric("Operational Blindspots", f"{blindspots}", "Missed in-house", delta_color="inverse")
        with c3: st.metric("Score: Resolved In-House", f"{avg_score_resolved:.1f}%" if avg_score_resolved > 0 else "0.0%", f"{len(resolved_group)} cases correlated")
        with c4: st.metric("Score: Unresolved In-House", f"{avg_score_failed:.1f}%" if avg_score_failed > 0 else "0.0%", f"{len(unresolved_group)} escalation slips", delta_color="inverse")

        # 8. Render Automated Synergy Distribution Analysis
        st.markdown("<div class='glass-container' style='margin-top: 40px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #1A1A1A; font-weight: 800; margin-bottom: 25px;'>Live Database Tracking: Sentiment Impact vs In-House Actions</h4>", unsafe_allow_html=True)
        
        action_analysis = ty_df.groupby('Operational_Status')['Score'].mean().reset_index().round(1)
        action_analysis = action_analysis[action_analysis['Operational_Status'] != 'No Match Found'].sort_values('Score', ascending=False)
        
        if not action_analysis.empty:
            fig = px.bar(
                action_analysis, y="Operational_Status", x="Score", orientation='h', color="Operational_Status",
                color_discrete_map={"Praise Logged": "#595733", "Issue Resolved In-House": "#7EC8BD", "Blindspot (Missed)": "#cf6231", "Issue Logged - Unresolved": "#8e2a2a"},
                text="Score"
            )
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False, xaxis=dict(range=[0, 100]), height=280, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Database integrated. Awaiting direct matching records across current data timeline profile indicators.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 9. Real Blindspot Analysis Output Grid
        st.markdown("<div class='glass-container' style='margin-top: 40px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #8e2a2a; font-weight: 800; margin-bottom: 10px;'>Active Operational Blindspots (Uncaptured Service Failures)</h4>", unsafe_allow_html=True)
        
        audit_records = negative_reviews[negative_reviews['Operational_Status'] == "Blindspot (Missed)"][['Published date', 'Author name', 'Score', 'Review Text']]
        st.dataframe(audit_records.sort_values('Score'), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Pipeline Execution Error: {e}")
