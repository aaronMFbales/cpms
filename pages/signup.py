import streamlit as st
# ...existing code...

import streamlit as st

st.set_page_config(page_title="CPMS - Account Information", page_icon="🏢", layout="wide")

# Clean CSS
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    div.block-container {
        padding: 60px 80px !important;
        margin: 40px auto !important;
        max-width: 800px !important;
        background: #fff;
        border-radius: 18px;
        box-shadow: 0 8px 32px rgba(44,62,80,0.10);
    }
    
    .main {
        padding: 40px !important;
        margin: 0 !important;
        background: #f6f8fa;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div style="background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0; text-align: center; font-size: 2.5rem; font-weight: bold;">
            🏢 MSME CPMS
        </h1>
        <p style="color: #bfdbfe; margin: 0.5rem 0 0 0; text-align: center; font-size: 1.1rem;">
            Client Profile Management System
        </p>
    </div>
""", unsafe_allow_html=True)

# Main content
st.markdown("## 📝 Account Information")

st.markdown("""
<div style='background-color: #f0f9ff; padding: 2rem; border-radius: 12px; border: 2px solid #3b82f6; margin: 2rem 0;'>
    <h3 style='color: #1e40af; margin: 0 0 1rem 0; text-align: center;'>🔒 Account Creation Policy</h3>
    <p style='font-size: 1.1rem; color: #374151; text-align: center; margin-bottom: 1.5rem;'>
        <strong>Encoder accounts are now created exclusively by system administrators.</strong>
    </p>
    
    <div style='background-color: white; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;'>
        <h4 style='color: #1e40af; margin: 0 0 1rem 0;'>📋 How to Get Access:</h4>
        <ol style='color: #374151; margin: 0; padding-left: 1.5rem;'>
            <li style='margin-bottom: 0.5rem;'><strong>Contact your administrator</strong> or focal person</li>
            <li style='margin-bottom: 0.5rem;'><strong>Provide your information:</strong> Name, email, organization, position</li>
            <li style='margin-bottom: 0.5rem;'><strong>Administrator creates your account</strong> with secure credentials</li>
            <li style='margin-bottom: 0.5rem;'><strong>Receive login credentials</strong> via email</li>
            <li style='margin-bottom: 0.5rem;'><strong>Login and start encoding data</strong> immediately</li>
        </ol>
    </div>
    
    <div style='background-color: #f0fdf4; padding: 1rem; border-radius: 8px; border-left: 4px solid #22c55e; margin: 1rem 0;'>
        <h4 style='color: #15803d; margin: 0 0 0.5rem 0;'>✅ Benefits of Admin-Created Accounts:</h4>
        <ul style='color: #374151; margin: 0; padding-left: 1.5rem;'>
            <li>No spam emails from account registrations</li>
            <li>Better security with controlled access</li>
            <li>Immediate account approval - no waiting period</li>
            <li>Centralized user management</li>
            <li>Secure password generation</li>
        </ul>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Contact information section
st.markdown("## 📞 Need Help?")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **For Account Creation:**
    - Contact your department's focal person
    - Reach out to the CPMS administrator
    - Provide necessary personal and work information
    """)

with col2:
    st.markdown("""
    **For Technical Support:**
    - Login issues
    - Password reset requests
    - System access problems
    """)

st.markdown("---")

# Back to login button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🔙 Back to Login Page", type="primary", use_container_width=True):
        st.switch_page("main.py")

st.markdown("""
<div style='text-align: center; margin-top: 2rem; padding: 1rem; background-color: #f8fafc; border-radius: 8px;'>
    <p style='color: #6b7280; margin: 0;'>
        <em>This change improves security and reduces administrative overhead for the CPMS system.</em>
    </p>
</div>
""", unsafe_allow_html=True)
