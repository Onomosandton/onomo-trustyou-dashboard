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

# 5. Header Layout Frame
aleph_img_tag = '<img src="data:image/png;base64,' + aleph_b64 + '" width="160" style="mix-blend-mode: multiply;">' if aleph_b64 else '<span style="font-weight:900; font-size:20px;">ALEPH</span>'
onomo_img_tag = '<img src="data:image/jpeg;base64,' + onomo_b64 + '" width="170" style="mix-blend-mode: multiply;">' if onomo_b64 else '<span style="font-weight:900; font-size:20px;">ONOMO</span>'

header_html = """
<div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0 30px 0; border-bottom: 1px solid rgba(0,0,0,0.05); margin-bottom: 40px;">
    <div style="flex: 1;">""" + aleph_img_tag + """</div>
    <div style="flex: 2; text-align: center;">
        <h2 style="margin: 0; color: #1A1A1A; font-weight: 900; letter-spacing: -0.5px; font-size: 2rem;">SYNERGY COMMAND CENTER</h2>
        <p style="margin: 5px 0 0 0; color: #7EC8BD; font-size: 0.95rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2.5px;">Sandton Property Operations</p>
    </div>
    <div style="flex: 1; display: flex; justify-content: flex-end;">""" + onomo_img_tag + """</div>
</div>"""

st.markdown(header_html, unsafe_allow_html=True)

if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

if st.session_state.uploaded_file is None:
    # --- STATE 1: THE WELCOME DASHBOARD PAGE ---
    welcome_left, welcome_right = st.columns([1.1, 1], gap="large")
    
    with welcome_left:
        st.markdown("<div style='padding-top: 30px;'></div>", unsafe_allow_html=True)
        st.markdown("<h1 style='color: #1A1A1A; font-weight: 900; font-size: 4rem; line-height: 1.05; letter-spacing: -1.5px; margin-bottom: 20px;'>Welcome to<br>Sandton Operations.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #666666; font-size: 1.25rem; line-height: 1.7; margin-bottom: 40px; max-width: 90%;'>Ignite the engine by uploading the latest weekly CSV report below. The system will instantly correlate guest sentiment with our on-the-ground floor trackers.</p>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Drop Weekly TrustYou CSV Here", type=["csv"], label_visibility="collapsed")
        if uploaded_file:
            st.session_state.uploaded_file = uploaded_file
            st.rerun()
            
    with welcome_right:
        img_src = "data:image/jpeg;base64," + vibe_b64 if vibe_b64 else "https://images.unsplash.com/photo-1542314831-c6a4d14d8c53?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
        image_html = """
        <div style="box-shadow: 0 20px 50px rgba(0,0,0,0.15); border-radius: 24px; overflow: hidden; margin-top: 10px;">
            <img src=\"""" + img_src + """\" style="width: 100%; display: block; object-fit: cover;">
        </div>"""
        st.markdown(image_html, unsafe_allow_html=True)

else:
    # --- STATE 2: ACTIVE HARD DATA ANALYTICS ---
    if st.button("← Reset Dashboard"):
        st.session_state.uploaded_file = None
        st.rerun()
        
    try:
        # Load and parse actual TrustYou data
        ty_df = pd.read_csv(st.session_state.uploaded_file)
        ty_df['Score'] = pd.to_numeric(ty_df['Score'], errors='coerce')
        ty_df['Published date'] = pd.to_datetime(ty_df['Published date'], errors='coerce').dt.tz_localize(None)
        
        # Fetch operational data
        fb_df = fetch_live_firebase_data()
        
        if not fb_df.empty and 'date' in fb_df.columns:
            fb_df['date'] = pd.to_datetime(fb_df['date'], errors='coerce').dt.tz_localize(None)
        
        # Exact Hard-coded Text Mining Correlation Matrix
        def correlate_real_operations(row, live_db):
            if live_db.empty:
                txt = str(row.get('Review Text', '')).lower()
                if any(w in txt for w in ['breakfast', 'menu', 'salt', 'mogodu', 'food', 'chef']): return "F&B Failure (Not Caught)"
                if any(w in txt for w in ['clean', 'dirty', 'housekeeping', 'sheets', 'stain']): return "Housekeeping Failure (Not Caught)"
                if any(w in txt for w in ['aircon', 'ac', 'tv', 'internet', 'wifi', 'broken', 'maintenance', 'phone', 'reception']): return "Maintenance Failure (Not Caught)"
                return "General Feedback"
                
            author_name = str(row['Author name']).lower().strip()
            review_date = row['Published date']
            if pd.isna(review_date) or author_name in ['nan', '']: return "General Feedback"
            
            time_window = (live_db['date'] <= review_date) & (live_db['date'] >= (review_date - timedelta(days=7)))
            active_window_logs = live_db[time_window]
            
            for _, fb_row in active_window_logs.iterrows():
                logged_identifier = str(fb_row['guestName']).lower()
                if author_name in logged_identifier or logged_identifier in author_name:
                    if fb_row['type'] == 'compliment': return "Praise Logged"
                    return "Issue Resolved In-House" if fb_row['status'] == 'resolved' else "Issue Logged - Unresolved"
            
            return "Blindspot (Missed)" if row['Score'] < 80 else "General Feedback"

        ty_df['Synergy_Status'] = ty_df.apply(lambda r: correlate_real_operations(r, fb_df), axis=1)
        
        # Analytics calculations
        total_reviews = len(ty_df)
        avg_score = ty_df['Score'].mean()
        
        failed_states = ["F&B Failure (Not Caught)", "Housekeeping Failure (Not Caught)", "Maintenance Failure (Not Caught)", "Blindspot (Missed)"]
        actual_blindspots = len(ty_df[ty_df['Synergy_Status'].isin(failed_states)])
        
        st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        with col1: st.metric("Reviews Correlated", f"{total_reviews}")
        with col2: st.metric("Overall TrustYou Score", f"{avg_score:.1f}%")
        with col3: st.metric("In-House Blindspots", f"{actual_blindspots}", "Missed opportunities before checkout", delta_color="inverse")
        with col4: st.metric("Operational Catch Rate", f"{((total_reviews - actual_blindspots)/total_reviews)*100:.1f}%", "Synergy baseline targets")
            
        # Chart Box Area
        st.markdown("<div class='glass-container' style='margin-top: 40px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #1A1A1A; font-weight: 800; margin-bottom: 25px;'>Synergy Analysis: TrustYou Sentiment Impact vs In-House Action</h4>", unsafe_allow_html=True)
        
        chart_df = ty_df.groupby('Synergy_Status')['Score'].mean().reset_index().round(1)
        chart_df = chart_df[chart_df['Synergy_Status'] != 'General Feedback'].sort_values('Score')
        
        if not chart_df.empty:
            fig = px.bar(
                chart_df, x="Score", y="Synergy_Status", orientation='h', color="Synergy_Status",
                color_discrete_sequence=["#8e2a2a", "#cf6231", "#333333", "#7EC8BD"], text="Score"
            )
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False, xaxis=dict(range=[0, 100]), height=280, margin=dict(l=0, r=0, t=10, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No departmental friction filters mapped across current data parameters.")
            
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Blindspots Table Grid Output
        st.markdown("<div class='glass-container' style='margin-top: 40px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #8e2a2a; font-weight: 800; margin-bottom: 10px;'>Active Operational Blindspots (Service Slips)</h4>", unsafe_allow_html=True)
        
        audit_df = ty_df[ty_df['Synergy_Status'].isin(failed_states)][['Published date', 'Author name', 'Synergy_Status', 'Score', 'Review Text']]
        st.dataframe(audit_df.sort_values('Score'), use_container_width=True, hide_index=True)
        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Pipeline Execution Failure: {e}")
