import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(
    page_title="Aleph Synergy Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Clean, Unblockable CSS
st.markdown("""
<style>
    /* Premium Light Grey Canvas */
    .stApp {
        background-color: #F8F9FA;
    }
    
    h1, h2, h3, h4, h5, h6, p, span, div {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Bulletproof Metric Cards */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        padding: 24px;
        border-radius: 8px;
        border-top: 4px solid #4A5D54; /* Aleph Deep Green */
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    
    div[data-testid="metric-container"] label {
        color: #4A5D54 !important;
        font-weight: 800 !important;
        font-size: 0.90rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #1A1A1A !important; 
        font-weight: 800 !important;
        font-size: 2.5rem !important;
    }

    /* Clean Uploader */
    section[data-testid="stFileUploadDropzone"] {
        background-color: #FFFFFF;
        border: 2px dashed #4A5D54;
        border-radius: 8px;
        padding: 30px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Header Section (Bulletproof Text for Aleph, Native Image for Onomo)
col_left, col_center, col_right = st.columns([1, 2, 1])

with col_left:
    st.markdown("""
        <div style='padding-top: 10px;'>
            <h2 style='color: #1A1A1A; font-weight: 900; margin: 0; letter-spacing: 1.5px;'>ALEPH</h2>
            <p style='color: #666666; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 2px; margin-top: -5px;'>Hospitality</p>
        </div>
    """, unsafe_allow_html=True)

with col_center:
    st.markdown("<h2 style='text-align: center; color: #1A1A1A; font-weight: 900; margin-bottom: 0;'>SYNERGY COMMAND CENTER</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #4A5D54; font-size: 0.9rem; font-weight: 800; text-transform: uppercase; letter-spacing: 2px;'>Sandton Property Operations</p>", unsafe_allow_html=True)

with col_right:
    # Your Onomo logo is working perfectly, so we keep it!
    st.image("Onomo-Johannesburg-Sandton-Logo-Horizontal-Black.jpg", width=180)

# 4. The Hero Banner (Native Streamlit Image - Will Never Be Blocked)
st.write("")
st.image("https://images.unsplash.com/photo-1542314831-c6a4d14d8c53?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80", use_column_width=True)
st.markdown("<p style='text-align: right; color: #999999; font-size: 0.75rem; margin-top: -10px; font-style: italic;'>Live Operational Environment Overlay</p>", unsafe_allow_html=True)

st.divider()

# 5. File Uploader & Data Logic
uploaded_file = st.file_uploader("Upload TrustYou / Floor Logs (CSV Format)", type=["csv"])

if uploaded_file is not None:
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
            
        st.write("")
        st.write("")
        
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
            color_discrete_sequence=["#1A1A1A", "#4A5D54", "#778B82", "#A9B5B0", "#333333"],
        )
        
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1A1A1A", size=14),
            showlegend=False,
            margin=dict(t=10, b=10, l=0, r=0)
        )
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#EAEAEA')
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        st.markdown("<h4 style='color: #1A1A1A; font-weight: 800;'>Correlated Data Audit</h4>", unsafe_allow_html=True)
        st.dataframe(df.head(10), use_container_width=True)

    except Exception as e:
        st.error(f"Error reading file: {e}")
        
else:
    st.markdown("<div style='background-color: #FFFFFF; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid #EAEAEA;'><p style='color: #1A1A1A; font-weight: 700; font-size: 1.1rem; margin: 0;'>Awaiting data. Please upload the latest CSV report above to populate the Command Center.</p></div>", unsafe_allow_html=True)
