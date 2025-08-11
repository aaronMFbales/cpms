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
try:
    st.set_page_config(
        page_title="DTI CPMS",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
except Exception as e:
    # Handle duplicate page config calls
    pass

# Add cache busting and error handling for JS module issues
if os.getenv('RENDER'):
    st.markdown("""
        <script>
        // Force reload if JS modules fail to load
        window.addEventListener('error', function(e) {
            if (e.message && e.message.includes('Failed to fetch dynamically imported module')) {
                console.log('JS module error detected, attempting cache refresh...');
                // Clear cache and reload
                if ('caches' in window) {
                    caches.keys().then(function(names) {
                        names.forEach(function(name) {
                            caches.delete(name);
                        });
                    });
                }
                // Add cache busting parameter
                setTimeout(function() {
                    window.location.href = window.location.href.split('?')[0] + '?cb=' + new Date().getTime();
                }, 1000);
            }
        });
        </script>
    """, unsafe_allow_html=True)

def main():
    # Ensure data directory exists
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Clean up expired sessions on startup
    try:
        session_manager.cleanup_expired_sessions()
    except Exception as e:
        print(f"Session cleanup error: {e}")
    
    # Initialize session state for authentication
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    
    if "auth_cookie" not in st.session_state:
        st.session_state["auth_cookie"] = None
    
    # Load session for current browser/device
    if not st.session_state["authenticated"]:
        try:
            saved_session = session_manager.load_session()
            if saved_session and saved_session.get("authenticated"):
                st.session_state["authenticated"] = True
                st.session_state["auth_cookie"] = saved_session
        except Exception as e:
            print(f"Session load error: {e}")
    else:
        # Update session activity for authenticated users
        try:
            auth_cookie = st.session_state.get("auth_cookie")
            if auth_cookie:
                # Update the session timestamp to reflect current activity
                session_manager.save_session(auth_cookie)
        except Exception as e:
            print(f"Session update error: {e}")

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
