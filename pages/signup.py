import streamlit as st
import time
import json
import os
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from utils.admin_config import get_default_admin_user, create_admin_if_not_exists

def hash_password(password):
    """Hash password for security"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from JSON file"""
    users_file = "data/users.json"
    if os.path.exists(users_file):
        try:
            with open(users_file, 'r') as f:
                users = json.load(f)
                # Ensure admin user exists
                created, message = create_admin_if_not_exists(users)
                if created:
                    save_users(users)
                return users
        except:
            return get_default_admin_user()
    else:
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

def send_registration_notification(user_data):
    """Send email notification to admin when a new user registers"""
    try:
        # Email configuration - using Streamlit secrets
        sender_email = st.secrets.get("email", {}).get("sender_email", "aaronmfbales@gmail.com")
        sender_password = st.secrets.get("email", {}).get("sender_password", "")
        receiver_email = st.secrets.get("email", {}).get("sender_email", "aaronmfbales@gmail.com")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = "New User Registration - CPMS"
        
        # Email body (removed location details)
        body = f"""
        New User Registration Notification
        
        A new user has registered for the CPMS system.
        
        User Details:
        - Name: {user_data.get('first_name', '')} {user_data.get('last_name', '')}
        - Username: {user_data.get('username', '')}
        - Email: {user_data.get('email', '')}
        - Organization: {user_data.get('organization', '')}
        - Position: {user_data.get('position', '')}
        - Contact Number: {user_data.get('contact_number', '')}
        - Registration Date: {datetime.fromtimestamp(user_data.get('created_at', time.time())).strftime('%Y-%m-%d %H:%M:%S')}
        
        Please log in to the admin panel to approve or reject this user.
        
        Best regards,
        CPMS System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Create SMTP session
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        
        return True
    except Exception as e:
        st.error(f"Failed to send email notification: {str(e)}")
        return False

st.set_page_config(page_title="CPMS Sign Up", page_icon="", layout="wide")

# Hide Streamlit elements and style
hide_st_style = """
    <style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stButton>button {
    background-color: #f0f0f0;
    color: black;
    border: none;
    transition: background-color 0.3s ease;
}
.stButton>button:hover {
    background-color: #1a2b5c;
    color: white;
}
/* Add small margins for breathing room */
div.block-container {
    padding: 20px !important;
    margin: 0 !important;
    max-width: none !important;
}
.main .block-container {
    padding: 20px !important;
    margin: 0 !important;
    max-width: none !important;
}
/* Remove sidebar spacing */
section[data-testid="stSidebar"] {
    display: none !important;
}
/* Full width content with small padding */
.main {
    padding: 20px !important;
    margin: 0 !important;
}
span[data-baseweb="form-control-caption"] {
    display: none !important;
}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

st.markdown("<h2 style='text-align: left; color: #263d81; font-weight: bold; font-size: 40px;'>ACCOUNT REGISTRATION</h2>", unsafe_allow_html=True)

# Create a 3-column layout for the form
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Personal Information")
    first_name = st.text_input("First Name", key="first_name")
    last_name = st.text_input("Last Name", key="last_name")
    email = st.text_input("Email Address", key="email")

with col2:
    st.markdown("### Account Information")
    username = st.text_input("Username", key="username")
    password = st.text_input("Password", type="password", key="password")
    confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")

with col3:
    st.markdown("### Organization Information")
    organization = st.text_input("Organization/Department", key="organization")
    position = st.text_input("Position/Title", key="position")
    contact_number = st.text_input("Contact Number", key="contact_number")

# Terms and Conditions - Full width
st.markdown("### Terms and Conditions")
agree_terms = st.checkbox("I agree to the terms and conditions", key="agree_terms")

col1, col2 = st.columns(2)
with col1:
    submit = st.button("Register", use_container_width=True)
with col2:
    back_to_login = st.button("Back to Login", use_container_width=True)

if submit:
    # Validation
    errors = []
    
    if not first_name or not last_name or not email or not username or not password:
        errors.append("All fields are required")
    
    if password != confirm_password:
        errors.append("Passwords do not match")
    
    if len(password) < 6:
        errors.append("Password must be at least 6 characters long")
    
    if not agree_terms:
        errors.append("You must agree to the terms and conditions")
    
    # Check if username already exists
    users = load_users()
    if username in users:
        errors.append("Username already exists")
    
    # Check if email already exists
    for user_data in users.values():
        if user_data.get("email") == email:
            errors.append("Email already registered")
            break
    
    if errors:
        for error in errors:
            st.error(error)
    else:
        # Create new user account (pending approval)
        new_user = {
            "password": hash_password(password),
            "role": "encoder",
            "approved": False,
            "created_at": time.time(),
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "organization": organization,
            "position": position,
            "contact_number": contact_number
        }
        
        users[username] = new_user
        save_users(users)
        
        # Send email notification to admin
        email_sent = send_registration_notification(new_user)
        
        # Show success message
        st.success("Input saved, thank you!")
        st.info("Your account is pending approval by the administrator.")
        st.info("You will be notified via email when your account is approved.")
        
        if email_sent:
            st.success("Email notification sent to administrator.")
        else:
            st.warning("Registration successful, but email notification failed.")
        
        # Add option to go back to login
        if st.button("Go Back to Login", use_container_width=True):
            st.switch_page("main.py")

if back_to_login:
    st.switch_page("main.py")
