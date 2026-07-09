import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration (No Emojis)
st.set_page_config(
    page_title="Aleph Synergy Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Ultra-Clean Corporate CSS
st.markdown("""
<style>
    /* Clean White Background */
    .stApp {
        background-color: #FFFFFF;
    }
    
    /* Sharp Corporate Typography */
    h1, h2, h3, h4, h5, h6, p, span, div {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Metric Cards - Minimalist with Aleph Portfolio Green Accent */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        padding: 20px;
        border-top: 4px solid #778B82; /* Muted teal/green from Aleph site */
        border-bottom: 1px solid #EAEAEA;
        border-left: 1px solid #EAEAEA;
        border-right: 1px solid #EAEAEA;
        box-shadow: none;
    }
    
    /* Metric Labels */
    div[data-testid="metric-container"] label {
        color: #666666 !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Metric Values - Thin and Sharp */
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #1A1A1A !important; 
        font-weight: 300 !important;
        font-size: 2.5rem !important;
    }

    /* Uploader Styling - Clean and Professional */
    section[data-testid="stFileUploadDropzone"] {
        background-color: #F8F9FA;
        border: 1px dashed #CCCCCC;
        border-radius: 4px;
        padding: 30px;
    }
    
    /* Subtle Divider */
    hr {
        border-top: 1px solid #EAEAEA !important;
        margin: 2em 0;
    }
</style>
""", unsafe_allow_html=True)

# 3. Header Section with Actual Logos
col_left, col_center, col_right = st.columns([1, 2, 1])

with col_left:
    # Pulling the Aleph logo directly using the exact GitHub UUID filename
    st.image("3ec1afe8-cd02-43ff-95aa-80b35415a9d1.png", width=160)

with col_center:
    st.markdown("<h2 style='text-align: center; color: #1A1A1A; font-weight: 700; margin-bottom: 0;'>SYNERGY COMMAND CENTER</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #778B82; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1.5px;'>Sandton Property Operations</p>", unsafe_allow_html=True)

with col_right:
    # Pulling the Onomo logo directly from your uploaded file
    st.image("Onomo-Johannesburg-Sandton-Logo-Horizontal-Black.jpg", width=180)

st.divider()

# 4. File Uploader (No Emojis)
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
            
        st.divider()
        
        # 6. Interactive Visualizations (Strict Corporate Palette)
        st.markdown("<h4 style='color: #1A1A1A; margin-bottom: 20px;'>Departmental Friction Heatmap</h4>", unsafe_allow_html=True)
        
        # Dummy data for layout
        chart_data = pd.DataFrame({
            "Department": ["Front Desk", "Housekeeping", "Food & Beverage", "Maintenance", "Spa"],
            "Incidents": [12, 18, 9, 24, 3]
        })
        
        # Bar Chart using Charcoal and the Aleph Green
        fig = px.bar(
            chart_data, 
            x="Department", 
            y="Incidents",
            color="Department",
            color_discrete_sequence=["#1A1A1A", "#778B82", "#333333", "#A9B5B0", "#555555"],
        )
        
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1A1A1A"),
            showlegend=False,
            margin=dict(t=10, b=10, l=0, r=0)
        )
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#EAEAEA')
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # 7. Raw Data Preview
        st.markdown("<h4 style='color: #1A1A1A; margin-bottom: 20px;'>Correlated Data Audit</h4>", unsafe_allow_html=True)
        st.dataframe(df.head(10), use_container_width=True)

    except Exception as e:
        st.error(f"Error reading file: {e}")
        
else:
    st.markdown("<p style='text-align: center; color: #666666; margin-top: 2em;'>Awaiting data. Please upload the latest CSV report above to populate the dashboard.</p>", unsafe_allow_html=True)
