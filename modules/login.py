import streamlit as st
from PIL import Image
import numpy as np
import time
import json
import os
import hashlib
from utils.admin_config import get_default_admin_user, create_admin_if_not_exists
from utils.secure_session import session_manager

def load_users():
    """Load users from JSON file"""
    users_file = "data/users.json"
    if os.path.exists(users_file):
        try:
            with open(users_file, 'r') as f:
                users = json.load(f)
                print(f"Loaded {len(users)} users: {list(users.keys())}")  # Debug print
                
                # Ensure admin user exists
                created, message = create_admin_if_not_exists(users)
                if created:
                    print(f"Admin check: {message}")
                    save_users(users)  # Save if admin was created
                
                return users
        except Exception as e:
            print(f"Error loading users: {e}")  # Debug print
            return get_default_admin_user()
    else:
        print(f"Users file not found at: {users_file}")  # Debug print
        # Initialize with admin user
        admin_user = get_default_admin_user()
        save_users(admin_user)
        return admin_user

def save_users(users):
    """Save users to JSON file"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    users_file = os.path.join(data_dir, "users.json")
    with open(users_file, 'w') as f:
        json.dump(users, f, indent=2)

def show():
    st.set_page_config(page_title="CPMS Login", layout="centered")

    # Robust CSS with specific targeting for login page only
    login_css = """
        <style>
        /* Login page specific CSS - use unique selectors to avoid conflicts */
        .login-page-container #MainMenu {visibility: hidden;}
        .login-page-container footer {visibility: hidden;}
        .login-page-container header {visibility: hidden;}
        
        /* Hide the entire app header including profile - login page only */
        .login-page-container div[data-testid="stAppViewContainer"] > section:first-child {
            display: none !important;
        }
        
        /* Hide Streamlit's top toolbar - login page only */
        .login-page-container .stAppToolbar {
            display: none !important;
        }
        
        /* Hide deploy button and GitHub info - login page only */
        .login-page-container .stActionButton {
            display: none !important;
        }
        
        /* Hide sidebar on login page only */
        .login-page-container section[data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* Hide sidebar toggle button - login page only */
        .login-page-container [data-testid="collapsedControl"] {
            display: none !important;
        }
        
        /* Hide any custom sidebar elements - login page only */
        .login-page-container .custom-sidebar {
            display: none !important;
        }
        
        /* Login button styling - specific to login page */
        .login-page-container .stButton>button {
            width: 30%;
            float: right;
            margin-right: 100px;
            background-color: #f0f0f0;
            color: black;
            border: none;
            transition: background-color 0.3s ease;
        }
        .login-page-container .stButton>button:hover {
            background-color: #1a2b5c;
            color: white;
        }
        
        /* Move entire content upward - login page only */
        .login-page-container div.block-container {
            padding-top: 20px !important;
        }
        
        /* Hide various Streamlit elements - login page specific */
        .login-page-container span[data-baseweb="form-control-caption"],
        .login-page-container div[data-testid="stAppViewContainer"] > div:first-child,
        .login-page-container div[data-testid="stAppViewBlockContainer"] > div:first-child,
        .login-page-container div[data-testid="stBottom"],
        .login-page-container header[data-testid="stHeader"],
        .login-page-container .st-emotion-cache-18ni7ap,
        .login-page-container .st-emotion-cache-6qob1r,
        .login-page-container .stAppDeployButton,
        .login-page-container div[data-testid="stAppDeployButton"],
        .login-page-container a[href*="streamlit.io"],
        .login-page-container .st-emotion-cache-h4xjwg,
        .login-page-container .stAppViewBlockContainer > div:last-child,
        .login-page-container div[class*="floating"],
        .login-page-container div[class*="badge"] {
            display: none !important;
        }
        
        /* Reset any inherited styles that might interfere */
        .login-page-container {
            background: white;
            min-height: 100vh;
        }
        </style>
    """
    
    # Apply login page CSS with container wrapper (use unique key to prevent conflicts)
    st.markdown(login_css, unsafe_allow_html=True)
    
    # Clear any previous page states that might interfere
    if 'selected_nav_item' in st.session_state:
        del st.session_state['selected_nav_item']
    if 'selected_sheet' in st.session_state:
        del st.session_state['selected_sheet']
    
    # Wrap everything in a container div for CSS targeting
    st.markdown('<div class="login-page-container">', unsafe_allow_html=True)

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        st.switch_page("modules/dashboard.py")  # ⬅️ Redirect to dashboard

    # Center everything using a single centered column
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Center the logo
        logo_path = "assets/dtilogo.png"
        st.image(logo_path, width=500)  

        # Center the title with slight left adjustment
        st.markdown(
            "<h4 style='text-align: center; color: #263d81; font-weight: bold; font-size: 30px; white-space: nowrap; margin-left: -210px;'>"
            "DTI REGION XI - CLIENT PERFORMANCE MONITORING SYSTEM"
            "</h4>",
            unsafe_allow_html=True
        )

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            col1, col2 = st.columns(2)
            with col1:
                login = st.form_submit_button("Login", use_container_width=True)
            with col2:
                signup = st.form_submit_button("Sign Up", use_container_width=True)

        if login:
            # Load users and check credentials
            users = load_users()
            print(f"Login attempt for username: {username}")  # Debug print
            print(f"Available users: {list(users.keys())}")  # Debug print
            
            if username in users:
                user_data = users[username]
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                
                if user_data["password"] == hashed_password:
                    if user_data.get("approved", False):
                        st.session_state["authenticated"] = True
                        # Set authentication cookie with timestamp
                        auth_data = {
                            "authenticated": True,
                            "timestamp": time.time(),
                            "username": username,
                            "role": user_data.get("role", "encoder"),
                            "first_name": user_data.get("first_name", ""),
                            "last_name": user_data.get("last_name", "")
                        }
                        st.session_state["auth_cookie"] = auth_data
                        
                        # Save session using secure session manager (per-browser)
                        session_manager.save_session(auth_data)
                        
                        st.success(f"Login successful! Welcome {username} ({user_data.get('role', 'encoder')})")
                        # Redirect based on role
                        if user_data.get("role") == "admin":
                            st.switch_page("pages/admin.py")
                        else:
                            # For encoder users, redirect to main.py which will show dashboard
                            st.rerun()
                    else:
                        st.error("Your account is pending approval. Please contact the administrator.")
                else:
                    st.error("Invalid password")
            else:
                st.error("Username not found")
        
        if signup:
            st.switch_page("pages/signup.py")

    st.markdown("</div>", unsafe_allow_html=True)
