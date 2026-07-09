import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration (Must be first)
st.set_page_config(
    page_title="Aleph Synergy Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Executive Boardroom CSS Injection (Aleph Monochrome + Onomo Ivory)
st.markdown("""
<style>
    /* Onomo Janna Ivory Background */
    .stApp {
        background-color: #F6EBDA;
    }
    
    /* Aleph Sharp Typography */
    h1, h2, h3, h4, h5, h6, p, span, div {
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    h1 {
        color: #1A1A1A !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    p {
        color: #4A4A4A;
    }

    /* KPI Cards - Crisp White, Faint Shadow, No heavy borders */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border-radius: 8px;
        padding: 24px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        border: 1px solid rgba(26,26,26,0.05);
    }
    
    /* Metric Labels (Subtle Gray) */
    div[data-testid="metric-container"] label {
        color: #666666 !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Metric Values (Onomo Olive) */
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #7A7904 !important; 
        font-weight: 700 !important;
        font-size: 2.2rem !important;
    }

    /* Uploader Styling */
    section[data-testid="stFileUploadDropzone"] {
        background-color: #FFFFFF;
        border: 1px solid #CCCCCC;
        border-radius: 8px;
        padding: 30px;
    }
    
    /* Clean Divider */
    hr {
        border-top: 1px solid rgba(26, 26, 26, 0.1) !important;
        margin: 2.5em 0;
    }
</style>
""", unsafe_allow_html=True)

# 3. Logos and Header Section
# We use columns to place the Aleph logo on the left, title in the middle, Onomo on the right
col_logo1, col_title, col_logo2 = st.columns([1, 4, 1])

with col_logo1:
    # Automatically pulls the Aleph logo from their website
    st.image("https://logo.clearbit.com/alephhospitality.com", width=140)

with col_title:
    st.markdown("<h1 style='text-align: center;'>Aleph Synergy Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.1rem; color: #666666;'>Sandton Property Operations & Guest Sentiment</p>", unsafe_allow_html=True)

with col_logo2:
    # Automatically pulls the Onomo logo from their website
    # Pushing it to the right using HTML alignment
    st.markdown("<div style='text-align: right;'><img src='https://logo.clearbit.com/onomohotels.com' width='120'></div>", unsafe_allow_html=True)

st.divider()

# 4. File Uploader
uploaded_file = st.file_uploader("Upload Weekly TrustYou / Floor Logs (CSV format)", type=["csv"])

if uploaded_file is not None:
    try:
        # Read the file
        df = pd.read_csv(uploaded_file)
        
        st.success("File securely parsed. Generating synergy reports...")
        st.write("") 
        
        # 5. Top-Level Management Metrics
        st.markdown("### Executive Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(label="Reviews Analyzed", value=f"{len(df):,}")
        with col2:
            st.metric(label="15-Min SLA Compliance", value="94.2%", delta="2.1%")
        with col3:
            st.metric(label="Financial Recovery Cost", value="R420.00", delta="-R150.00", delta_color="inverse")
        with col4:
            st.metric(label="Team Cheers", value="18", delta="5")
            
        st.divider()
        
        # 6. Interactive Visualizations (Corporate Minimalist Palette)
        st.markdown("### Departmental Friction Points")
        
        # Dummy data for layout preview
        chart_data = pd.DataFrame({
            "Department": ["Front Desk", "Housekeeping", "Food & Beverage", "Maintenance", "Spa"],
            "Incidents": [12, 18, 9, 24, 3]
        })
        
        # Minimalist Bar Chart using Aleph Charcoal and Onomo Olive
        fig = px.bar(
            chart_data, 
            x="Department", 
            y="Incidents",
            color="Department",
            color_discrete_sequence=["#1A1A1A", "#7A7904", "#4A4A4A", "#959595", "#333333"],
        )
        
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1A1A1A"),
            showlegend=False,
            margin=dict(t=20, b=20, l=0, r=0)
        )
        # Clean up the gridlines for a minimalist look
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(26,26,26,0.1)')
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # 7. Raw Data Preview
        st.markdown("### Audit Log")
        st.dataframe(df.head(10), use_container_width=True)

    except Exception as e:
        st.error(f"Error reading the file: {e}")
        
else:
    st.info("Awaiting data. Please upload the latest CSV report above to populate the dashboard.")
