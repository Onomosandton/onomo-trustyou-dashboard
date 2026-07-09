# 3. Bulletproof Text-Based Header Section
col_left, col_title, col_right = st.columns([1, 4, 1])

with col_left:
    # Bulletproof Aleph Branding
    st.markdown("""
        <div style='text-align: left; padding-top: 15px;'>
            <span style='font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 14px; font-weight: 800; color: #1A1A1A; letter-spacing: 1px; text-transform: uppercase;'>
                Aleph
            </span><br>
            <span style='font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 10px; font-weight: 400; color: #666666; letter-spacing: 2px; text-transform: uppercase;'>
                Hospitality
            </span>
        </div>
    """, unsafe_allow_html=True)

with col_title:
    st.markdown("<h1 style='text-align: center;'>Aleph Synergy Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.1rem; color: #666666;'>Sandton Property Operations & Guest Sentiment</p>", unsafe_allow_html=True)

with col_right:
    # Bulletproof Onomo Branding using their signature Olive color
    st.markdown("""
        <div style='text-align: right; padding-top: 15px;'>
            <span style='font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 16px; font-weight: 900; color: #7A7904; letter-spacing: 1.5px; text-transform: uppercase;'>
                ONOMO
            </span><br>
            <span style='font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; font-size: 10px; font-weight: 500; color: #959595; letter-spacing: 2px; text-transform: uppercase;'>
                Hotels
            </span>
        </div>
    """, unsafe_allow_html=True)

st.divider()
