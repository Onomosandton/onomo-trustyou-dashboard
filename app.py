import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Aleph Synergy Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Forced Background & Glassmorphism CSS
st.markdown("""
<style>
    /* Force the background image using Streamlit's new container IDs */
    [data-testid="stAppViewContainer"] {
        background-image: linear-gradient(rgba(255, 255, 255, 0.4), rgba(255, 255, 255, 0.7)), 
                          url('https://images.unsplash.com/photo-1542314831-c6a4d14d8c53?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Make the top header bar transparent so it doesn't block the image */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }
    
    /* Sharp Corporate Typography */
    h1, h2, h3, h4, h5, h6, p, span, div {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Invert the Aleph logo colors (White to Black) */
    div[data-testid="column"]:nth-of-type(1) img {
        filter: invert(1);
    }
    
    /* Metric Cards - Frosted Glass Effect */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.75) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        padding: 20px;
        border-radius: 12px;
        border-top: 5px solid #4A5D54; /* Aleph Corporate Deep Green */
        border-left: 1px solid rgba(255,255,255,0.6);
        border-right: 1px solid rgba(255,255,255,0.6);
        border-bottom: 1px solid rgba(255,255,255,0.6);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.15);
    }
    
    /* Metric Labels */
    div[data-testid="metric-container"] label {
        color: #4A5D54 !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Metric Values */
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #1A1A1A !important; 
        font-weight: 800 !important;
        font-size: 2.8rem !important;
    }

    /* Uploader Styling - Glassmorphism */
    section[data-testid="stFileUploadDropzone"] {
        background: rgba(255, 255, 255, 0.65) !important;
        backdrop-filter: blur(12px) !important;
        border: 2px dashed #4A5D54;
        border-radius: 12px;
        padding: 30px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
    }
    
    /* Custom Glass Containers for Charts and Data */
    .glass-container {
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255,255,255,0.6);
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Header Section
col_left, col_center, col_right = st.columns([1, 2, 1])

with col_left:
    # Adding a try/except visual fallback in case the filename is still slightly off
    try:
        st.image("3ec1afe8-cd02-43ff-95aa-80b35415a9d1.png", width=160)
    except:
        st.error("Aleph Logo file not found. Check exact GitHub name/extension.")

with col_center:
    st.markdown("<h2 style='text-align: center; color: #1A1A1A; font-weight: 900; margin-bottom: 0; text-shadow: 0px 2px 10px rgba(255,255,255,0.9);'>SYNERGY COMMAND CENTER</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #4A5D54; font-size: 1rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; text-shadow: 0px 1px 5px rgba(255,255,255,0.8);'>Sandton Property Operations</p>", unsafe_allow_html=True)

with col_right:
    st.image("Onomo-Johannesburg-Sandton-Logo-Horizontal-Black.jpg", width=180)

st.divider()

# 4. File Uploader
uploaded_file = st.file_uploader("Upload TrustYou / Floor Logs (CSV Format)", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        
        # 5. Top-Level Management Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(label="Reviews Analyzed", value=f"{len(df):,}")
        with col2:
            st.metric(label="SLA Compliance", value="94.2%", delta="2.1%")
        with col3:
            st.metric(label="Recovery Cost", value="R420", delta="-R150", delta_color="inverse")
        with col4:
            st.metric(label="Staff Highlights", value="18", delta="5")
            
        # 6. Interactive Visualizations inside Glass Containers
        st.markdown("<div class='glass-container'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #1A1A1A; margin-bottom: 20px; font-weight: 800;'>Departmental Friction Heatmap</h4>", unsafe_allow_html=True)
        
        chart_data = pd.DataFrame({
            "Department": ["Front Desk", "Housekeeping", "Food & Beverage", "Maintenance", "Spa"],
            "Incidents": [12, 18, 9, 24, 3]
        })
        
        # Aleph Corporate Palette: Deep Greens and Charcoals
        fig = px.bar(
            chart_data, 
            x="Department", 
            y="Incidents",
            color="Department",
            color_discrete_sequence=["#1A1A1A", "#4A5D54", "#778B82", "#A9B5B0", "#333333"],
        )
        
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1A1A1A", size=14),
            showlegend=False,
            margin=dict(t=10, b=10, l=0, r=0)
        )
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(74, 93, 84, 0.2)')
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # 7. Raw Data Preview inside Glass Container
        st.markdown("<div class='glass-container' style='margin-top: 30px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #1A1A1A; margin-bottom: 20px; font-weight: 800;'>Correlated Data Audit</h4>", unsafe_allow_html=True)
        st.dataframe(df.head(10), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error reading file: {e}")
        
else:
    st.markdown("<div class='glass-container'><p style='text-align: center; color: #1A1A1A; font-weight: 800; font-size: 1.2rem; margin: 0;'>Awaiting data. Please upload the latest CSV report above to ignite the engine.</p></div>", unsafe_allow_html=True)
