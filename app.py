import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration (Must be the first command)
st.set_page_config(
    page_title="Synergy Engine | Onomo Hotel",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. African Fusion & Onomo Brand CSS Injection
st.markdown("""
<style>
    /* Warm Ivory Background with subtle gradient */
    .stApp {
        background-color: #f6ebda;
        background-image: radial-gradient(circle at 100% 100%, rgba(241, 138, 0, 0.08) 0%, transparent 40%), 
                          radial-gradient(circle at 0% 0%, rgba(0, 48, 64, 0.05) 0%, transparent 40%);
    }
    
    /* Header Typography - Deep Navy */
    h1, h2, h3 {
        color: #003040 !important;
        font-family: 'Arial', sans-serif;
        font-weight: 800 !important;
    }
    
    /* Subtext */
    p {
        color: #334155;
        font-size: 1.1rem;
    }

    /* The 'O-Smile' Orange Accent */
    .accent-orange {
        color: #f18a00;
    }

    /* Metric Cards - Clean White with Orange Border */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.04);
        border-left: 8px solid #f18a00;
        transition: transform 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 20px rgba(0,0,0,0.08);
    }
    
    /* Metric Numbers */
    div[data-testid="metric-container"] label {
        color: #003040 !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #8e2a2a !important; /* Rich Terracotta for numbers */
        font-weight: 900 !important;
    }

    /* Divider */
    hr {
        border-top: 2px solid rgba(241, 138, 0, 0.3) !important;
        margin: 2em 0;
    }
    
    /* File Uploader Styling */
    section[data-testid="stFileUploadDropzone"] {
        background-color: rgba(255, 255, 255, 0.7);
        border: 2px dashed #003040;
        border-radius: 16px;
    }
    section[data-testid="stFileUploadDropzone"]:hover {
        background-color: rgba(241, 138, 0, 0.1);
        border-color: #f18a00;
    }
</style>
""", unsafe_allow_html=True)

# 3. Vibrant Header Section
st.markdown("<h1>🌍 <span class='accent-orange'>Aleph Synergy Engine</span></h1>", unsafe_allow_html=True)
st.markdown("### 🦓 *Where African Hospitality Meets Operational Excellence*")
st.write("Welcome to the GM Command Center. Drop your TrustYou CSV below to instantly map online guest sentiment to our live floor operations.")
st.divider()

# 4. File Uploader
uploaded_file = st.file_uploader("📂 Drop Weekly TrustYou / Floor Logs Here (CSV format)", type=["csv"])

if uploaded_file is not None:
    try:
        # Read the file
        df = pd.read_csv(uploaded_file)
        
        st.success("✨ File securely parsed in local memory! Generating synergy reports...")
        st.write("") # Spacer
        
        # 5. Top-Level Management Metrics
        st.markdown("### 📊 High-Level Performance Indicators")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(label="Total Reviews Analyzed", value=f"{len(df):,}")
        with col2:
            # Streamlit automatically adds the up/down arrows based on the + or - sign
            st.metric(label="15-Min SLA Compliance", value="94.2%", delta="2.1%")
        with col3:
            st.metric(label="Financial Recovery Cost", value="R420.00", delta="-R150.00", delta_color="inverse")
        with col4:
            st.metric(label="O-Smile Team Cheers", value="18", delta="5")
            
        st.divider()
        
        # 6. Interactive Visualizations (African Fusion Colors)
        st.markdown("### 🎯 Departmental Heat Map")
        
        # Dummy data placeholder for the visual
        chart_data = pd.DataFrame({
            "Department": ["Front Desk", "Housekeeping", "Food & Beverage", "Maintenance", "Spa"],
            "Friction Points": [12, 18, 9, 24, 3]
        })
        
        # Plotly Bar Chart with Onomo Colors
        fig = px.bar(
            chart_data, 
            x="Department", 
            y="Friction Points",
            color="Department",
            color_discrete_sequence=["#003040", "#f18a00", "#595733", "#cf6231", "#8e2a2a"],
            title="Weekly Friction Points by Department"
        )
        
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#003040", family="Arial"),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # 7. Raw Data Preview for Transparency
        st.markdown("### 🔍 Raw Data Audit Log")
        st.dataframe(df.head(10), use_container_width=True)

    except Exception as e:
        st.error(f"🚨 Oops! Error reading the file: {e}")
        
else:
    # Warm empty state
    st.info("👆 Waiting for data... Drop a CSV file above to ignite the engine.")
