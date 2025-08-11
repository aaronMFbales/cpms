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
    # Robust CSS with specific targeting for login page only
    login_css = """
        <style>
        /* Hide Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Hide sidebar completely on login page */
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        
        /* Hide sidebar toggle button */
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        
        /* Hide deploy button and other Streamlit branding */
        .stAppDeployButton,
        div[data-testid="stAppDeployButton"],
        .stAppToolbar,
        .stActionButton {
            display: none !important;
        }
        
        /* Login form input field width adjustment */
        .stTextInput > div > div > input {
            width: 70% !important;
            margin: 0 auto !important;
        }
        
        /* Login button styling */
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
        
        /* Move content upward */
        div.block-container {
            padding-top: 20px !important;
        }
        </style>
    """
    
    # Apply login page CSS
    st.markdown(login_css, unsafe_allow_html=True)
    
    # Clear any previous page states that might interfere
    if 'selected_nav_item' in st.session_state:
        del st.session_state['selected_nav_item']
    if 'selected_sheet' in st.session_state:
        del st.session_state['selected_sheet']

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        st.switch_page("modules/dashboard.py")  # ⬅️ Redirect to dashboard

    # Center everything using a single centered column - adjusted to move form left
    col1, col2, col3 = st.columns([1.3, 1, 1.2])
    with col2:
        # Center the logo
        logo_path = "assets/dtilogo.png"
        st.image(logo_path, width=350)  

        # Center the title with slight left adjustment
        st.markdown(
            "<h4 style='text-align: center; color: #263d81; font-weight: bold; font-size: 30px; white-space: nowrap; margin-left: -210px;'>"
            "DTI REGION XI - CLIENT PROFILE AND MONITORING SYSTEM"
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
            # Advanced character cleaning
            import re
            import unicodedata
            
            # Get raw input for debugging
            raw_username = username if username else ""
            raw_password = password if password else ""
            
            # Step 1: Unicode normalization
            username = unicodedata.normalize('NFKC', raw_username) if raw_username else ""
            password = unicodedata.normalize('NFKC', raw_password) if raw_password else ""
            
            # Step 2: Remove zero-width and invisible characters
            invisible_chars = [
                '\u200B',  # Zero-width space
                '\u200C',  # Zero-width non-joiner
                '\u200D',  # Zero-width joiner
                '\u2060',  # Word joiner
                '\uFEFF',  # Zero-width no-break space (BOM)
                '\u00AD',  # Soft hyphen
                '\u034F',  # Combining grapheme joiner
                '\u180E',  # Mongolian vowel separator
            ]
            
            for char in invisible_chars:
                username = username.replace(char, '')
                password = password.replace(char, '')
            
            # Step 3: Replace all Unicode whitespace with regular space, then strip
            username = re.sub(r'\s+', ' ', username).strip()
            password = re.sub(r'\s+', ' ', password).strip()
            
            # Step 4: Remove any remaining non-printable characters
            username = re.sub(r'[^\x20-\x7E]', '', username)
            password = re.sub(r'[^\x20-\x7E]', '', password)
            
            # Step 5: Final cleanup - remove any control characters
            username = ''.join(char for char in username if ord(char) >= 32 and ord(char) <= 126)
            password = ''.join(char for char in password if ord(char) >= 32 and ord(char) <= 126)
            
            # Load users and check credentials
            users = load_users()
            
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
