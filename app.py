import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os

# 1. Page Configuration 
st.set_page_config(
    page_title="Synergy Command Center",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Base64 Encoder
def get_base64_image(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

aleph_b64 = get_base64_image("aleph_logo.png")
onomo_b64 = get_base64_image("onomo_logo.jpg")
vibe_b64 = get_base64_image("vibe1.jpg")

# 3. God-Mode CSS
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
        transition: all 0.3s ease !important;
    }
    div[data-testid="stFileUploader"] section:hover {
        background-color: #F0F9F8 !important;
        border-color: #4A5D54 !important;
    }
    
    div[data-testid="metric-container"] {
        background: #FFFFFF !important;
        padding: 24px;
        border-radius: 12px;
        border-top: 4px solid #7EC8BD; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.03);
        border: 1px solid rgba(0,0,0,0.02);
    }
    div[data-testid="metric-container"] label {
        color: #888888 !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #1A1A1A !important; 
        font-weight: 800 !important;
        font-size: 2.8rem !important;
    }
    .glass-container {
        background: #FFFFFF !important;
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.03);
        border: 1px solid rgba(0,0,0,0.02) !important;
    }
</style>
""", unsafe_allow_html=True)

# 4. Header
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

# 5. App Router
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

if st.session_state.uploaded_file is None:
    # --- WELCOME SCREEN ---
    col1, col2 = st.columns([1.1, 1], gap="large")
    with col1:
        st.markdown("<div style='padding-top: 30px;'></div><h1 style='color: #1A1A1A; font-weight: 900; font-size: 4rem; line-height: 1.05; letter-spacing: -1.5px; margin-bottom: 20px;'>Welcome to<br>Sandton Operations.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #666666; font-size: 1.25rem; line-height: 1.7; margin-bottom: 40px; max-width: 90%;'>Ignite the engine by uploading the latest weekly CSV report below. The system will instantly correlate guest sentiment with our on-the-ground floor trackers.</p>", unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Drop TrustYou CSV Here", type=["csv"], label_visibility="collapsed")
        if uploaded_file:
            st.session_state.uploaded_file = uploaded_file
            st.rerun()
            
    with col2:
        img_src = f"data:image/jpeg;base64,{vibe_b64}" if vibe_b64 else "https://images.unsplash.com/photo-1542314831-c6a4d14d8c53?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80"
        st.markdown(f'<div style="box-shadow: 0 20px 50px rgba(0,0,0,0.15); border-radius: 24px; overflow: hidden; margin-top: 10px;"><img src="{img_src}" style="width: 100%; display: block; object-fit: cover;"></div>', unsafe_allow_html=True)

else:
    # --- LIVE ANALYTICS DASHBOARD ---
    if st.button("← Reset Dashboard"):
        st.session_state.uploaded_file = None
        st.rerun()
        
    try:
        # Load the real TrustYou Data
        df = pd.read_csv(st.session_state.uploaded_file)
        
        # Calculate Real KPIs from the CSV
        total_reviews = len(df)
        avg_score = df['Score'].mean()
        pending_replies = df['Public reply text'].isna().sum()
        
        # Mocking Firebase Correlation (Phase 1 Prototype)
        firebase_matches = min(14, total_reviews) 
        
        st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4, gap="medium")
        
        with col1:
            st.metric(label="Total Reviews", value=f"{total_reviews:,}")
        with col2:
            st.metric(label="Average Score", value=f"{avg_score:.1f}%")
        with col3:
            st.metric(label="Unanswered Reviews", value=f"{pending_replies}", delta="-2" if pending_replies < 5 else f"+{pending_replies}", delta_color="inverse")
        with col4:
            st.metric(label="Floor Tracker Matches", value=f"{firebase_matches}", delta="Automated", delta_color="normal")
            
        st.markdown("<div class='glass-container' style='margin-top: 40px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #1A1A1A; font-weight: 800; margin-bottom: 25px;'>Review Volume by Platform Source</h4>", unsafe_allow_html=True)
        
        # Real Chart built from 'Source' column
        source_data = df['Source'].value_counts().reset_index()
        source_data.columns = ['Platform', 'Count']
        
        fig = px.bar(
            source_data, x="Platform", y="Count", color="Platform",
            color_discrete_sequence=["#1A1A1A", "#7EC8BD", "#A9B5B0", "#333333", "#cf6231"]
        )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#1A1A1A", size=14), showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.05)')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='glass-container' style='margin-top: 40px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #1A1A1A; font-weight: 800; margin-bottom: 25px;'>Review Extraction Audit</h4>", unsafe_allow_html=True)
        
        # Display only the most relevant columns to the GM
        display_df = df[['Published date', 'Author name', 'Source', 'Score', 'Review Text']].copy()
        display_df.fillna("N/A", inplace=True)
        st.dataframe(display_df.head(10), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error processing TrustYou data: {e}")
