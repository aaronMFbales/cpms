import streamlit as st
from modules import login, dashboard
import time
import json
import os
from utils.secure_session import session_manager

# Render compatibility
if os.getenv('RENDER'):
    import render_config
    for key, value in render_config.config.items():
        st._config.set_option(key, value)

# Configure the page layout at the very beginning
st.set_page_config(
    page_title="DTI CPMS",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Clean up expired sessions on startup
    session_manager.cleanup_expired_sessions()
    
    # Initialize session state for authentication
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    
    if "auth_cookie" not in st.session_state:
        st.session_state["auth_cookie"] = None
    
    # Load session for current browser/device
    if not st.session_state["authenticated"]:
        saved_session = session_manager.load_session()
        if saved_session and saved_session.get("authenticated"):
            st.session_state["authenticated"] = True
            st.session_state["auth_cookie"] = saved_session

    if not st.session_state["authenticated"]:
        login.show()
    else:
        # Check user role and redirect accordingly
        auth_cookie = st.session_state.get("auth_cookie")
        if auth_cookie and auth_cookie.get("role") == "admin":
            st.switch_page("pages/admin.py")
        else:
            # For all approved users (admin and encoder), show dashboard
            dashboard.show()

if __name__ == "__main__":
    main()
