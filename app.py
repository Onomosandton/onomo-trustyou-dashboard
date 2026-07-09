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

# 2. Base64 HTML Image Renderer (Bypasses Streamlit's image wrappers)
def render_image(filepath, width, mix_blend=False, align="left"):
    if not os.path.exists(filepath):
        return f"<p style='color:red; font-size:12px;'>Missing: {filepath}</p>"
    
    with open(filepath, "rb") as f:
        data = base64.b64encode(f.read()).decode("utf-8")
    
    mime = "image/png" if filepath.lower().endswith(".png") else "image/jpeg"
    blend_style = "mix-blend-mode: multiply;" if mix_blend else ""
    
    if align == "right":
        align_style = "margin-left: auto; display: block;"
    elif align == "center":
        align_style = "margin: 0 auto; display: block;"
    else:
        align_style = "display: block;"
        
    return f'<img src="data:{mime};base64,{data}" style="width: {width}; {blend_style} {align_style}">'

# 3. Premium Corporate CSS
st.markdown("""
<style>
    /* Premium Light Canvas */
    .stApp {
        background-color: #F4F5F7;
    }
    
    /* Sharp Corporate Typography */
    h1, h2, h3, h4, h5, h6, p, span, div {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Transparent Header */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* Metric Cards */
    div[data-testid="metric-container"] {
        background: #FFFFFF !important;
        padding: 24px;
        border-radius: 8px;
        border-top: 4px solid #7EC8BD; 
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #EAEAEA;
    }
    
    div[data-testid="metric-container"] label {
        color: #666666 !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #1A1A1A !important; 
        font-weight: 800 !important;
        font-size: 2.5rem !important;
    }

    /* Uploader & Data Containers */
    .glass-container, section[data-testid="stFileUploadDropzone"] {
        background: #FFFFFF !important;
        border-radius: 8px;
        padding: 30px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #EAEAEA !important;
    }
    
    section[data-testid="stFileUploadDropzone"] {
        border: 2px dashed #7EC8BD !important; 
    }
</style>
""", unsafe_allow_html=True)

# 4. Persistent Header
col_logo1, col_title, col_logo2 = st.columns([1, 2, 1])

with col_logo1:
    # Applying the multiply blend mode directly to the HTML to melt the white background
    st.markdown(render_image("aleph_logo.png", width="160px", mix_blend=True, align="left"), unsafe_allow_html=True)

with col_title:
    st.markdown("<h2 style='text-align: center; color: #1A1A1A; font-weight: 900; margin-bottom: 0;'>SYNERGY COMMAND CENTER</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #7EC8BD; font-size: 1rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px;'>Sandton Property Operations</p>", unsafe_allow_html=True)

with col_logo2:
    # Applying the multiply blend mode and pushing to the right
    st.markdown(render_image("onomo_logo.jpg", width="180px", mix_blend=True, align="right"), unsafe_allow_html=True)

st.divider()

# 5. The Uploader
uploaded_file = st.file_uploader("Upload TrustYou / Floor Logs (CSV Format)", type=["csv"])

# 6. Dynamic State Router
if uploaded_file is None:
    # --- STATE 1: THE WELCOME SCREEN ---
    welcome_left, welcome_right = st.columns([1, 1.2])
    
    with welcome_left:
        st.markdown("<br><br><h1 style='color: #1A1A1A; font-weight: 800;'>Welcome to Sandton Operations.</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #666666; font-size: 1.2rem; line-height: 1.6;'>Ignite the engine by uploading the latest weekly CSV report above. The system will automatically correlate guest sentiment with our on-the-ground floor trackers.</p>", unsafe_allow_html=True)
    
    with welcome_right:
        # Render the lifestyle image cleanly without any Streamlit captions
        st.markdown(render_image("vibe1.jpg", width="100%", mix_blend=False, align="center"), unsafe_allow_html=True)

else:
    # --- STATE 2: THE ACTIVE DASHBOARD ---
    try:
        df = pd.read_csv(uploaded_file)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(label="Reviews Analyzed", value=f"{len(df):,}")
        with col2:
            st.metric(label="SLA Compliance", value="94.2%", delta="2.1%")
        with col3:
            st.metric(label="Recovery Cost", value="R420", delta="-R150", delta_color="inverse")
        with col4:
            st.metric(label="Staff Highlights", value="18", delta="5")
            
        st.markdown("<div class='glass-container' style='margin-top: 30px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #1A1A1A; font-weight: 800;'>Departmental Friction Heatmap</h4>", unsafe_allow_html=True)
        
        chart_data = pd.DataFrame({
            "Department": ["Front Desk", "Housekeeping", "Food & Beverage", "Maintenance", "Spa"],
            "Incidents": [12, 18, 9, 24, 3]
        })
        
        fig = px.bar(
            chart_data, 
            x="Department", 
            y="Incidents",
            color="Department",
            color_discrete_sequence=["#1A1A1A", "#7EC8BD", "#A9B5B0", "#333333", "#666666"],
        )
        
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1A1A1A", size=14),
            showlegend=False,
            margin=dict(t=10, b=10, l=0, r=0)
        )
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(26,26,26,0.1)')
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='glass-container' style='margin-top: 30px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #1A1A1A; font-weight: 800;'>Correlated Data Audit</h4>", unsafe_allow_html=True)
        st.dataframe(df.head(10), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error reading file: {e}")
