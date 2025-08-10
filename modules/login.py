import streamlit as st
from PIL import Image
import numpy as np
import time
import json
import os
import hashlib
from utils.admin_config import get_default_admin_user, create_admin_if_not_exists

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
    st.set_page_config(page_title="CPMS Login", page_icon="🛡️", layout="centered")

    # Hide Streamlit elements and style the button
    hide_st_style = """
        <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hide the entire app header including profile */
    div[data-testid="stAppViewContainer"] > section:first-child {
        display: none !important;
    }
    
    /* Hide Streamlit's top toolbar */
    .stAppToolbar {
        display: none !important;
    }
    
    /* Hide deploy button and GitHub info */
    .stActionButton {
        display: none !important;
    }
    
    /* Hide sidebar on login page */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* Hide sidebar toggle button */
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    
    /* Hide any custom sidebar elements */
    .custom-sidebar {
        display: none !important;
    }
    
    .stButton>button {
        width: 30%;
        float: right;
        margin-right: 100px;
        background-color: #f0f0f0;
        color: black;
        border: none;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1a2b5c;
        color: white;
    }
    /* Move entire content upward */
    div.block-container {
        padding-top: 20px !important;
    }
    /* Hide Streamlit's "Please Enter to apply" helper text */
    span[data-baseweb="form-control-caption"] {
        display: none !important;
    }
    
    /* Hide profile and creator information */
    div[data-testid="stAppViewContainer"] > div:first-child {
        display: none !important;
    }
    
    /* Hide GitHub profile badge/info */
    div[data-testid="stAppViewBlockContainer"] > div:first-child {
        display: none !important;
    }
    
    /* Hide any footer or creator attribution */
    div[data-testid="stBottom"] {
        display: none !important;
    }
    
    /* Hide Streamlit's default app header */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    /* Alternative selectors to hide profile info */
    .st-emotion-cache-18ni7ap,
    .st-emotion-cache-6qob1r,
    [data-testid="stAppViewContainer"] > div:nth-child(1) {
        display: none !important;
    }
    
    /* Hide any "created by" or attribution text */
    div:contains("created by"),
    div:contains("Aaron Bales"),
    small:contains("created by"),
    p:contains("created by") {
        display: none !important;
    }
    
    /* Hide Streamlit's "Hosted with Streamlit" badge */
    .stAppDeployButton,
    div[data-testid="stAppDeployButton"],
    a[href*="streamlit.io"],
    div:contains("Hosted with Streamlit"),
    [data-testid="stBottom"],
    .st-emotion-cache-h4xjwg {
        display: none !important;
    }
    
    /* Hide any floating badges or promotional content */
    .stAppViewBlockContainer > div:last-child,
    div[class*="floating"],
    div[class*="badge"] {
        display: none !important;
    }
    </style>
    """
    st.markdown(hide_st_style, unsafe_allow_html=True)

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
                        
                        # Save session to file for persistence
                        session_file = "session.json"
                        with open(session_file, 'w') as f:
                            json.dump(auth_data, f)
                        
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
