import streamlit as st
from modules import login, dashboard
import time
import json
import os

# Configure the page layout at the very beginning
st.set_page_config(
    page_title="CPMS Dashboard", 
    layout="wide",
    initial_sidebar_state="auto"
)

def main():
    # Initialize session state for authentication
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    
    # Check for existing authentication cookiez``
    if "auth_cookie" not in st.session_state:
        st.session_state["auth_cookie"] = None
    
    # Check for persistent session file
    session_file = "session.json"
    if os.path.exists(session_file):
        try:
            with open(session_file, 'r') as f:
                saved_session = json.load(f)
                if saved_session.get("authenticated") and saved_session.get("timestamp"):
                    current_time = time.time()
                    if current_time - saved_session["timestamp"] < 86400:  # 24 hours
                        st.session_state["authenticated"] = True
                        st.session_state["auth_cookie"] = saved_session
                        # Update timestamp
                        saved_session["timestamp"] = current_time
                        with open(session_file, 'w') as f:
                            json.dump(saved_session, f)
                    else:
                        # Session expired, remove file
                        os.remove(session_file)
        except:
            pass

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
