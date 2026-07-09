import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Aleph Synergy Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Immersive CSS with Real Background & Glassmorphism
st.markdown("""
<style>
    /* Inject Real Hospitality Background Image with a subtle brightening overlay for readability */
    .stApp {
        background-image: linear-gradient(rgba(255, 255, 255, 0.6), rgba(255, 255, 255, 0.8)), 
                          url('https://images.unsplash.com/photo-1542314831-c6a4d14d8c53?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Sharp Corporate Typography */
    h1, h2, h3, h4, h5, h6, p, span, div {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Magic Fix: Invert the Aleph logo colors (White to Black) */
    div[data-testid="column"]:nth-of-type(1) img {
        filter: invert(1);
    }
    
    /* Metric Cards - Frosted Glass Effect with Aleph Deep Green */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px); /* The frosted glass blur */
        -webkit-backdrop-filter: blur(12px);
        padding: 20px;
        border-radius: 10px;
        border-top: 5px solid #4A5D54; /* Aleph Corporate Deep Green */
        border-left: 1px solid rgba(255,255,255,0.5);
        border-right: 1px solid rgba(255,255,255,0.5);
        border-bottom: 1px solid rgba(255,255,255,0.5);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
    }
    
    /* Metric Labels */
    div[data-testid="metric-container"] label {
        color: #4A5D54 !important;
        font-weight: 700 !important;
        font-size: 0.90rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Metric Values */
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #1A1A1A !important; 
        font-weight: 300 !important;
        font-size: 2.8rem !important;
    }

    /* Uploader Styling - Glassmorphism */
    section[data-testid="stFileUploadDropzone"] {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border: 2px dashed #4A5D54;
        border-radius: 10px;
        padding: 30px;
    }
    
    /* Glass Data Containers */
    .glass-container {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255,255,255,0.5);
        margin-top: 20px;
    }
    
    hr {
        border-top: 1px solid rgba(74, 93, 84, 0.2) !important;
        margin: 2em 0;
    }
</style>
""", unsafe_allow_html=True)

# 3. Header Section
col_left, col_center, col_right = st.columns([1, 2, 1])

with col_left:
    st.image("3ec1afe8-cd02-43ff-95aa-80b35415a9d1.png", width=160)

with col_center:
    st.markdown("<h2 style='text-align: center; color: #1A1A1A; font-weight: 800; margin-bottom: 0; text-shadow: 0px 2px 4px rgba(255,255,255,0.8);'>SYNERGY COMMAND CENTER</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #4A5D54; font-size: 1rem; font-weight: 600; text-transform: uppercase; letter-spacing: 2px;'>Sandton Property Operations</p>", unsafe_allow_html=True)

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
        st.markdown("<h4 style='color: #1A1A1A; margin-bottom: 20px; font-weight: 700;'>Departmental Friction Heatmap</h4>", unsafe_allow_html=True)
        
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
            plot_bgcolor="rgba(255,255,255,0.2)",
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
        st.markdown("<h4 style='color: #1A1A1A; margin-bottom: 20px; font-weight: 700;'>Correlated Data Audit</h4>", unsafe_allow_html=True)
        st.dataframe(df.head(10), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error reading file: {e}")
        
else:
    st.markdown("<div class='glass-container'><p style='text-align: center; color: #1A1A1A; font-weight: 600; font-size: 1.2rem; margin: 0;'>Awaiting data. Please upload the latest CSV report above to ignite the engine.</p></div>", unsafe_allow_html=True)
