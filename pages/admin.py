import streamlit as st
import time
import json
import os
import hashlib
import smtplib
import secrets
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from utils.admin_config import get_default_admin_user, create_admin_if_not_exists, get_admin_credentials_display
from utils.secure_session import session_manager

def hash_password(password):
    """Hash password for security"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_secure_password(length=6):
    """Generate a secure random password"""
    # Simple character set: uppercase, lowercase, and digits only
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def send_account_creation_email(user_data, password):
    """Send email with account credentials to new encoder"""
    try:
        # Email configuration - using Streamlit secrets (support both formats)
        email_config = st.secrets.get("email", {})
        sender_email = email_config.get("sender_email") or email_config.get("username") or email_config.get("from", "")
        sender_password = email_config.get("sender_password") or email_config.get("password", "")
        receiver_email = user_data.get('email', '')
        
        if not receiver_email:
            st.warning("No email address provided for the user.")
            return False
            
        if not sender_email or not sender_password:
            st.warning("Email credentials not configured in Streamlit secrets. Please configure email settings to send credentials automatically.")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = "CPMS Account Created - Login Credentials"
        
        # Email body
        body = f"""Dear {user_data.get('first_name', '')} {user_data.get('last_name', '')},

Your CPMS (Client Profile Management System) account has been created by the administrator.

Login Credentials:
Username: {user_data.get('username', '')}
Password: {password}

Personal Information:
Name: {user_data.get('first_name', '')} {user_data.get('last_name', '')}
Email: {user_data.get('email', '')}
Organization: {user_data.get('organization', '')}
Position: {user_data.get('position', '')}
Contact: {user_data.get('contact_number', '')}

IMPORTANT SECURITY NOTICE:
- Please change your password after your first login
- Keep your credentials secure and do not share them
- Your account is automatically approved and ready to use

You can now log in to the CPMS system using the provided credentials.

Best regards,
CPMS Administration Team"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Create SMTP session and send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        st.warning("Email authentication failed. Please check your Gmail credentials and app password settings.")
        st.info("To fix this: Go to Google Account settings → Security → App passwords → Generate new app password")
        return False
    except (ConnectionRefusedError, OSError) as e:
        st.warning("Network connection failed. Please check your internet connection and firewall settings.")
        st.info("This error often occurs when SMTP ports (587/465) are blocked by corporate firewalls.")
        return False
    except Exception as e:
        st.warning(f"Email delivery failed: {str(e)}")
        return False

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

def backup_deleted_user(username, user_data):
    """Backup deleted user data"""
    try:
        data_dir = "data"
        backup_file = os.path.join(data_dir, "deleted_users_backup.json")
        
        # Load existing backup or create new one
        if os.path.exists(backup_file):
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)
        else:
            backup_data = {}
        
        # Add deleted user to backup with deletion timestamp
        backup_data[username] = {
            **user_data,
            "deleted_at": time.time(),
            "deleted_by": "admin"
        }
        
        # Save backup
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        return True
    except Exception as e:
        st.error(f"Failed to backup deleted user: {str(e)}")
        return False

def load_deleted_users_backup():
    """Load deleted users backup"""
    data_dir = "data"
    backup_file = os.path.join(data_dir, "deleted_users_backup.json")
    
    if os.path.exists(backup_file):
        try:
            with open(backup_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def restore_user_from_backup(username, backup_data):
    """Restore user from backup"""
    try:
        users = load_users()
        
        # Get user data from backup
        user_data = backup_data[username].copy()
        
        # Remove backup-specific fields
        user_data.pop("deleted_at", None)
        user_data.pop("deleted_by", None)
        
        # Add back to active users
        users[username] = user_data
        save_users(users)
        
        return True
    except Exception as e:
        st.error(f"Failed to restore user: {str(e)}")
        return False

def format_timestamp(timestamp):
    """Format timestamp to readable date"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def get_active_users():
    """Get list of currently active/online users"""
    try:
        active_users = []
        sessions_dir = "data/sessions"
        current_time = time.time()
        
        if not os.path.exists(sessions_dir):
            return []
        
        # Load all users to get user details
        users = load_users()
        
        for filename in os.listdir(sessions_dir):
            if filename.startswith('session_') and filename.endswith('.json'):
                filepath = os.path.join(sessions_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        session_data = json.load(f)
                    
                    # Check if session is active (within last 30 minutes for online status)
                    time_diff = current_time - session_data.get('timestamp', 0)
                    
                    if time_diff <= 1800:  # 30 minutes
                        username = session_data.get('username')
                        if username and username in users:
                            user_info = users[username]
                            
                            # Determine status based on last activity
                            if time_diff <= 300:  # 5 minutes - Online
                                status = 'online'
                                status_text = 'Online'
                            elif time_diff <= 900:  # 15 minutes - Away
                                status = 'away' 
                                status_text = 'Away'
                            else:  # Up to 30 minutes - Idle
                                status = 'idle'
                                status_text = 'Idle'
                            
                            active_users.append({
                                'username': username,
                                'full_name': f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip(),
                                'role': user_info.get('role', 'encoder'),
                                'status': status,
                                'status_text': status_text,
                                'last_activity': session_data.get('timestamp', 0),
                                'browser_id': session_data.get('browser_id', 'unknown'),
                                'session_start': session_data.get('created_at', 'unknown')
                            })
                except:
                    continue
        
        # Sort by last activity (most recent first)
        active_users.sort(key=lambda x: x['last_activity'], reverse=True)
        return active_users
        
    except Exception as e:
        return []

def format_time_ago(timestamp):
    """Format time difference as 'X minutes ago' """
    current_time = time.time()
    diff = current_time - timestamp
    
    if diff < 60:
        return "Just now"
    elif diff < 3600:
        minutes = int(diff / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif diff < 86400:
        hours = int(diff / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = int(diff / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"

# Configure page
st.set_page_config(
    page_title="MSME CPMS Admin Dashboard", 
    page_icon="", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hide Streamlit's default page navigation
st.markdown("""
<style>
    /* Hide the default Streamlit page navigation */
    [data-testid="stSidebarNav"] {
        display: none;
    }
    
    /* Hide the sidebar nav list */
    section[data-testid="stSidebar"] > div:first-child > div:first-child > div:first-child > div:first-child {
        display: none;
    }
    
    /* Modern Professional Sidebar Design - Matching Dashboard */
    .stSidebar {
        background: linear-gradient(180deg, #1e3a8a 0%, #172087 100%) !important;
        border-right: none !important;
        box-shadow: 2px 0 10px rgba(0,0,0,0.1) !important;
    }
    
    /* Hide resize handle */
    .stSidebar .css-1lcbmhc {
        display: none !important;
    }
    
    .stSidebar .sidebar-content {
        padding: 0 !important;
    }
    
    /* Make all sidebar text white */
    .stSidebar * {
        color: white !important;
    }
    
    /* Sidebar titles and headers */
    .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4, .stSidebar h5, .stSidebar h6 {
        color: white !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar text elements */
    .stSidebar p, .stSidebar div, .stSidebar span, .stSidebar label {
        color: white !important;
    }
    
    /* Navigation buttons */
    .stSidebar button {
        color: white !important;
        background-color: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 6px !important;
        width: 100% !important;
        text-align: left !important;
        padding: 1px 1px !important;
        margin: 3px 0 !important;
        transition: all 0.3s ease !important;
        font-weight: 500 !important;
        font-size: 0.9em !important;
    }
    
    /* Navigation button hover */
    .stSidebar button:hover {
        background-color: rgba(255,255,255,0.2) !important;
        color: white !important;
        transform: translateX(2px) !important;
        border-left: 3px solid #60a5fa !important;
    }
    
    /* Primary button (selected state) */
    .stSidebar button[data-baseweb="button"][kind="primary"] {
        background-color: rgba(255,255,255,0.25) !important;
        border-left: 3px solid #60a5fa !important;
        font-weight: 600 !important;
    }
    
    /* Metrics styling */
    .stSidebar [data-testid="metric-container"] {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 8px !important;
        padding: 8px !important;
    }
    
    .stSidebar [data-testid="metric-container"] * {
        color: white !important;
    }
    
    /* Dividers */
    .stSidebar hr {
        border-color: rgba(255,255,255,0.2) !important;
        margin: 16px 0 !important;
    }
    
    /* Main content area professional styling */
    .main .block-container {
        padding: 0 1rem 1rem !important;
        max-width: 100% !important;
    }
    
    /* Override the negative margin compensation */
    .main {
        padding-top: 10px !important;
    }
    
    /* Professional headers with enhanced gradient */
    .admin-header {
        background: linear-gradient(to right, 
            #0f1659 0%, 
            #172087 35%, 
            #1e3a8a 60%, 
            #1d4ed8 90%, 
            #3b82f6 120%);
        color: white;
        padding: 30px 40px 25px 40px;
        margin: -20px -20px 20px -20px;
        border-radius: 0 0 15px 15px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.4), 
                    0 4px 16px rgba(29, 78, 216, 0.3),
                    inset 0 1px 0 rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .admin-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(45deg, 
            rgba(255,255,255,0.15) 0%, 
            transparent 30%, 
            rgba(59, 130, 246, 0.1) 50%,
            transparent 70%, 
            rgba(255,255,255,0.08) 100%);
        pointer-events: none;
    }
    
    .admin-header h1 {
        margin: 0;
        font-size: 2.2em;
        font-weight: 700;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.5), 
                     0 0 20px rgba(59, 130, 246, 0.3);
        letter-spacing: 0.5px;
        line-height: 1.1;
        position: relative;
        z-index: 1;
    }
    
    .admin-header p {
        margin: 10px 0 0 0;
        font-size: 1.1em;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.4), 
                     0 0 15px rgba(59, 130, 246, 0.2);
        font-weight: 400;
        letter-spacing: 0.3px;
        opacity: 0.95;
        position: relative;
        z-index: 1;
    }
    
    /* Content section styling */
    .content-section {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border: 1px solid #e5e7eb;
    }
    
    .content-section h2 {
        color: #1f2937;
        font-weight: 600;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 0.5rem;
    }
    
    .content-section h3 {
        color: #374151;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
    }
    
    /* Form styling */
    .stForm {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    /* Button enhancements */
    .stButton button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        border: none;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
    }
    
    .stButton button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
    
    /* Info boxes */
    .stInfo {
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
    }
    
    .stSuccess {
        border-radius: 8px;
        border-left: 4px solid #10b981;
    }
    
    .stError {
        border-radius: 8px;
        border-left: 4px solid #ef4444;
    }
    
    .stWarning {
        border-radius: 8px;
        border-left: 4px solid #f59e0b;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: #f8fafc;
        border-radius: 8px;
        font-weight: 500;
    }
    
    /* Ensure our custom navigation is at the top */
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Session validation
if "authenticated" not in st.session_state or not st.session_state.get("authenticated"):
    try:
        saved_session = session_manager.load_session()
        if saved_session and saved_session.get("authenticated") and saved_session.get("role") == "admin":
            st.session_state["authenticated"] = True
            st.session_state["auth_cookie"] = saved_session
        else:
            st.error("Access denied. Admin privileges required.")
            st.markdown("[← Go back to login page](../)")
            st.stop()
    except Exception as e:
        st.error("Access denied. Admin privileges required.")
        st.markdown("[← Go back to login page](../)")
        st.stop()

auth_cookie = st.session_state.get("auth_cookie")
if not auth_cookie or auth_cookie.get("role") != "admin":
    st.error("Access denied. Admin privileges required.")
    st.markdown("[← Go back to login page](../)")
    st.stop()

# Header section with professional styling
st.markdown("""
    <div class="admin-header">
        <h1>MSME CPMS ADMIN DASHBOARD</h1>
        <p>Client Profile Management System - Administrative Control Panel</p>
    </div>
""", unsafe_allow_html=True)

# Initialize navigation state
if "admin_selected_tab" not in st.session_state:
    if auth_cookie and 'current_admin_tab' in auth_cookie:
        st.session_state["admin_selected_tab"] = auth_cookie['current_admin_tab']
    else:
        st.session_state["admin_selected_tab"] = "Create Encoder Account"

selected_tab = st.session_state.get("admin_selected_tab", "Create Encoder Account")

# Update session
try:
    current_tab = st.session_state.get("admin_selected_tab", "Create Encoder Account") 
    auth_cookie['current_admin_tab'] = current_tab
    session_manager.save_session(auth_cookie)
except Exception as e:
    pass

# Sidebar Navigation
with st.sidebar:
    # Simple professional header
    st.title("CPMS Admin")
    st.caption("Administrative Control Panel")
    
    st.subheader("Navigation")
    
    # Navigation buttons
    admin_tabs = [
        ("Create Encoder Account", ""),
        ("Manage Encoder Accounts", ""),
        ("Active Sessions", ""),
        ("System Settings", "")
    ]
    
    for tab_name, icon in admin_tabs:
        button_selected = selected_tab == tab_name
        if st.button(f"{tab_name}", key=f"sidebar_nav_{tab_name}", use_container_width=True, 
                    type="primary" if button_selected else "secondary"):
            st.session_state.admin_selected_tab = tab_name
            st.rerun()
    
    st.divider()
    
    # Quick Stats
    users = load_users()
    active_users = get_active_users()
    total_encoders = len([u for u in users.values() if u.get("role") == "encoder"])
    online_count = len([u for u in active_users if u['status'] == 'online'])
    
    st.subheader("System Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Encoders", total_encoders)
        st.metric("Online Now", online_count)
    with col2:
        st.metric("Admin Sessions", 1)
    
    st.divider()
    
    # Admin Profile
    admin_name = f"{auth_cookie.get('first_name', 'Admin')} {auth_cookie.get('last_name', '')}"
    st.subheader("Admin Profile")
    st.write(f"**Name:** {admin_name}")
    st.write(f"**Role:** {auth_cookie.get('role', 'admin').title()}")
    st.write(f"**Status:** Online")
    
    st.divider()
    
    # Logout button
    if st.button("Logout", type="primary", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["auth_cookie"] = None
        session_manager.clear_session()
        st.switch_page("main.py")

# Main content area based on selected tab
if selected_tab == "Create Encoder Account":
    st.markdown("## Create New Encoder Account")
    st.markdown("Create accounts for encoders who will be entering data into the CPMS system.")
    
    with st.form("create_encoder_form"):
        st.markdown("### Personal Information")
        
        # Personal info in organized columns
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name *", help="Encoder's first name", placeholder="Enter first name")
            last_name = st.text_input("Last Name *", help="Encoder's last name", placeholder="Enter last name")
            email = st.text_input("Email Address *", help="Valid email address for sending credentials", placeholder="name@example.com")
            
        with col2:
            username = st.text_input("Username *", help="Unique username for login", placeholder="Choose a username")
            organization = st.text_input("Organization/Department", help="Organization or department", placeholder="Organization name")
            position = st.text_input("Position/Title", help="Job position or title", placeholder="Job title")
        
        contact_number = st.text_input("Contact Number", help="Phone number (optional)", placeholder="+63 XXX XXX XXXX")
        
        st.markdown("---")
        st.markdown("### Security Configuration")
        st.info("A secure 6-character password will be automatically generated for this account.")
        st.markdown("**Password will include:**")
        st.markdown("- Uppercase and lowercase letters")
        st.markdown("- Numbers")
        st.markdown("- No special characters for better compatibility")
        
        st.markdown("---")
        st.markdown("### Notification Settings")
        send_email = st.checkbox("Send credentials via email", value=True, 
                                help="Automatically email the login credentials to the encoder")
        
        col_submit1, col_submit2 = st.columns([3, 1])
        with col_submit2:
            submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)
        
        if submitted:
            # Enhanced validation with better user feedback
            errors = []
            
            # Required field validation
            if not first_name.strip():
                errors.append("First name is required")
            if not last_name.strip():
                errors.append("Last name is required")
            if not email.strip():
                errors.append("Email address is required")
            if not username.strip():
                errors.append("Username is required")
            
            # Email format validation
            import re
            if email.strip() and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                errors.append("Please enter a valid email address")
            
            # Username validation
            if username.strip() and (len(username) < 3 or not username.replace('_', '').isalnum()):
                errors.append("Username must be at least 3 characters and contain only letters, numbers, and underscores")
            
            # Check for existing users
            existing_users = load_users()
            if username.strip().lower() in [k.lower() for k in existing_users.keys()]:
                errors.append("Username already exists - please choose a different username")
            
            for user_data in existing_users.values():
                if user_data.get("email", "").lower() == email.strip().lower():
                    errors.append("Email address is already registered with another account")
                    break
            
            # Display validation errors
            if errors:
                st.error("Please correct the following issues:")
                for error in errors:
                    st.error(f"• {error}")
            else:
                # Generate secure password automatically
                password = generate_secure_password()
                st.success(f"**Generated Password: `{password}`**")
                st.info("This password has been automatically generated and will be sent via email.")
                
                # Verify password is set
                if not password:
                    st.error("**Critical Error:** Password is empty! Cannot create account.")
                    st.stop()
                
                # Show the password prominently
                st.markdown("---")
                st.markdown("### **Account Credentials**")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Username:** `{username}`")
                with col2:
                    st.markdown(f"**Password:** `{password}`")
                st.markdown("---")
                
                # Create new encoder account with timestamp
                new_encoder = {
                    "username": username.strip(),  # Add username to the data
                    "password": hash_password(password),
                    "role": "encoder",
                    "approved": True,
                    "active": True,
                    "created_at": time.time(),
                    "created_by": auth_cookie.get("username", "admin"),
                    "first_name": first_name.strip(),
                    "last_name": last_name.strip(),
                    "email": email.strip().lower(),
                    "organization": organization.strip() if organization else "",
                    "position": position.strip() if position else "",
                    "contact_number": contact_number.strip() if contact_number else ""
                }
                
                # Save to database
                existing_users[username.strip()] = new_encoder
                save_users(existing_users)
                
                # Success display with professional styling
                st.success("**Account Created Successfully!**")
                
                # Credentials display
                st.markdown("### **Account Summary**")
                st.info(f"""
                **New Encoder Account Details:**
                - **Name:** {first_name} {last_name}
                - **Username:** `{username}`
                - **Email:** {email}
                - **Organization:** {organization if organization else "N/A"}
                - **Position:** {position if position else "N/A"}
                """)
                
                # Email sending
                if send_email:
                    with st.spinner("Sending credentials via email..."):
                        email_sent = send_account_creation_email(new_encoder, password)
                    
                    if email_sent:
                        st.success("Login credentials have been sent to the encoder's email address!")
                    else:
                        st.warning("Account created successfully, but email delivery failed. Please share credentials manually.")
                        
                        # Show credentials when email fails
                        st.info("**Login Credentials (Share these manually):**")
                        st.code(f"""
Username: {username}
Password: {password}
                        """)
                        
                        # Provide troubleshooting guidance
                        with st.expander("Email Troubleshooting", expanded=False):
                            st.markdown("""
                            **Common email delivery issues:**
                            
                            1. **Network Connectivity**: Check internet connection and firewall settings
                            2. **SMTP Configuration**: Verify Gmail SMTP settings in secrets.toml
                            3. **App Password**: Ensure Gmail app password is correct and active
                            4. **Corporate Firewall**: Some networks block SMTP ports (587, 465)
                            
                            **Manual delivery options:**
                            - Copy the credentials above and send via secure communication
                            - Use the organization's internal email system
                            - Provide credentials through a secure password manager
                            """)
                
                # Next steps information
                st.markdown("---")
                with st.expander("Next Steps & Instructions", expanded=True):
                    st.markdown("""
                    **Account Status:** Active and ready to use
                    
                    **For the Encoder:**
                    1. Check email for login credentials
                    2. Log in to the CPMS system using provided username and password
                    3. Change password after first login (recommended)
                    4. Begin data entry tasks as assigned
                    
                    **For the Administrator:**
                    - Account is immediately available in 'Manage Encoder Accounts'
                    - Monitor activity in 'Active Sessions' tab
                    - Reset password or manage account as needed
                    """)
    
    # Helpful note for creating additional accounts
    st.markdown("---")
    st.info("**Need to create another account?** Simply refresh this page (F5 or Ctrl+R) to clear the form and start fresh!")

elif selected_tab == "Manage Encoder Accounts":
    st.markdown("## Manage Encoder Accounts")
    st.markdown("View, edit, and manage all encoder accounts in the system.")
    
    users = load_users()
    encoder_users = {k: v for k, v in users.items() if v.get("role") == "encoder"}
    
    if not encoder_users:
        st.info("No encoder accounts found. Create the first encoder account using the 'Create Encoder Account' tab.")
    else:
        st.markdown(f"### Total Encoder Accounts: {len(encoder_users)}")
        
        # Search functionality
        search_term = st.text_input("Search encoders", placeholder="Search by name, username, or email...")
        
        # Filter users based on search
        filtered_users = encoder_users
        if search_term:
            filtered_users = {
                k: v for k, v in encoder_users.items() 
                if search_term.lower() in k.lower() or 
                   search_term.lower() in v.get('first_name', '').lower() or
                   search_term.lower() in v.get('last_name', '').lower() or
                   search_term.lower() in v.get('email', '').lower()
            }
        
        # Display encoder accounts
        for username, user_data in filtered_users.items():
            user_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
            display_name = user_name if user_name else username
            created_date = format_timestamp(user_data.get('created_at', 0))
            
            with st.expander(f"{display_name} ({username}) - Created: {created_date}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown("**Personal Information**")
                    st.write(f"**Name:** {user_data.get('first_name', '')} {user_data.get('last_name', '')}")
                    st.write(f"**Email:** {user_data.get('email', 'N/A')}")
                    st.write(f"**Organization:** {user_data.get('organization', 'N/A')}")
                    st.write(f"**Position:** {user_data.get('position', 'N/A')}")
                    st.write(f"**Contact:** {user_data.get('contact_number', 'N/A')}")
                    
                with col2:
                    st.markdown("**Account Details**")
                    st.write(f"**Username:** {username}")
                    st.write(f"**Role:** {user_data.get('role', 'encoder').title()}")
                    st.write(f"**Status:** Active")
                    st.write(f"**Created:** {created_date}")
                    if user_data.get('created_by'):
                        st.write(f"**Created by:** {user_data.get('created_by')}")
                
                with col3:
                    st.markdown("**Actions**")
                    
                    # Delete Account (with confirmation)
                    if st.button("Delete Account", key=f"delete_{username}", type="secondary"):
                        st.session_state[f"confirm_delete_{username}"] = True
                    
                    # Confirmation for deletion
                    if st.session_state.get(f"confirm_delete_{username}", False):
                        st.warning("Are you sure you want to delete this account?")
                        col_yes, col_no = st.columns(2)
                        
                        with col_yes:
                            if st.button("Yes, Delete", key=f"confirm_yes_{username}"):
                                # Backup before deletion
                                backup_deleted_user(username, user_data)
                                del users[username]
                                save_users(users)
                                st.session_state[f"confirm_delete_{username}"] = False
                                st.success(f"Account '{username}' deleted successfully!")
                                st.rerun()
                        
                        with col_no:
                            if st.button("Cancel", key=f"confirm_no_{username}"):
                                st.session_state[f"confirm_delete_{username}"] = False
                                st.rerun()

elif selected_tab == "Active Sessions":
    st.markdown("## Active Sessions")
    st.markdown("Monitor who is currently using the CPMS system.")
    
    # Get active users data
    active_users = get_active_users()
    
    # Auto-refresh functionality
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.metric("Active Users", len(active_users))
    with col2:
        auto_refresh = st.checkbox("Auto-refresh (30s)", value=False)
    with col3:
        if st.button("Refresh Now"):
            st.rerun()
    
    # Auto-refresh timer
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    if not active_users:
        st.info("No users are currently active.")
        st.markdown("---")
        st.markdown("**Status Definitions:**")
        st.markdown("- **Online:** Active within last 5 minutes")
        st.markdown("- **Away:** Active within last 15 minutes") 
        st.markdown("- **Idle:** Active within last 30 minutes")
    else:
        # Group users by status
        online_users = [u for u in active_users if u['status'] == 'online']
        away_users = [u for u in active_users if u['status'] == 'away']
        idle_users = [u for u in active_users if u['status'] == 'idle']
        
        # Status tabs
        tab1, tab2, tab3 = st.tabs([
            f"Online ({len(online_users)})",
            f"Away ({len(away_users)})", 
            f"Idle ({len(idle_users)})"
        ])
        
        with tab1:
            if online_users:
                for user in online_users:
                    st.markdown(f"""
                    **{user['full_name']}** (`{user['username']}`)  
                    Online - {user['role'].title()} - Last activity: {format_time_ago(user['last_activity'])}
                    """)
                    st.divider()
            else:
                st.info("No users currently online.")
        
        with tab2:
            if away_users:
                for user in away_users:
                    st.markdown(f"""
                    **{user['full_name']}** (`{user['username']}`)  
                    Away - {user['role'].title()} - Last activity: {format_time_ago(user['last_activity'])}
                    """)
                    st.divider()
            else:
                st.info("No users currently away.")
        
        with tab3:
            if idle_users:
                for user in idle_users:
                    st.markdown(f"""
                    **{user['full_name']}** (`{user['username']}`)  
                    Idle - {user['role'].title()} - Last activity: {format_time_ago(user['last_activity'])}
                    """)
                    st.divider()
            else:
                st.info("No users currently idle.")

elif selected_tab == "System Settings":
    st.markdown("## System Settings")
    st.markdown("Configure system settings and view administrative information.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### System Information")
        users = load_users()
        total_users = len(users)
        encoder_count = len([u for u in users.values() if u.get("role") == "encoder"])
        admin_count = len([u for u in users.values() if u.get("role") == "admin"])
        
        st.metric("Total Users", total_users)
        st.metric("Encoder Accounts", encoder_count)
        st.metric("Admin Accounts", admin_count)
        
        st.markdown("### Admin Configuration")
        admin_info = get_admin_credentials_display()
        
        st.write(f"**Username:** `{admin_info['username']}`")
        st.write(f"**Email:** `{admin_info['email']}`")
        st.write(f"**Name:** {admin_info['name']}")
        st.info("Admin credentials are stored securely in Streamlit secrets")
    
    with col2:
        st.markdown("### System Tools")
        
        # Admin Password Change Section
        st.markdown("#### Configure Admin Password")
        st.markdown("Change your admin account password for enhanced security.")
        
        with st.form("change_admin_password"):
            current_password = st.text_input("Current Password", type="password", 
                                           help="Enter your current admin password", 
                                           placeholder="Enter current password")
            
            new_password = st.text_input("New Password", type="password", 
                                       help="Enter your new password (minimum 8 characters)", 
                                       placeholder="Enter new password")
            
            confirm_password = st.text_input("Confirm New Password", type="password", 
                                           help="Re-enter your new password", 
                                           placeholder="Confirm new password")
            
            change_password_submitted = st.form_submit_button("Change Password", type="primary")
            
            if change_password_submitted:
                # Validation
                errors = []
                
                # Check if all fields are filled
                if not current_password:
                    errors.append("Current password is required")
                if not new_password:
                    errors.append("New password is required")
                if not confirm_password:
                    errors.append("Password confirmation is required")
                
                # Password requirements
                if new_password and len(new_password) < 8:
                    errors.append("New password must be at least 8 characters long")
                
                if new_password and not any(c.isdigit() for c in new_password):
                    errors.append("New password should contain at least one number")
                
                if new_password and not any(c.isupper() for c in new_password):
                    errors.append("New password should contain at least one uppercase letter")
                
                # Check if new passwords match
                if new_password != confirm_password:
                    errors.append("New password and confirmation do not match")
                
                # Check if new password is different from current
                if current_password == new_password:
                    errors.append("New password must be different from current password")
                
                if errors:
                    st.error("Please correct the following issues:")
                    for error in errors:
                        st.error(f"• {error}")
                else:
                    # Verify current password
                    users = load_users()
                    current_admin_username = auth_cookie.get("username")
                    
                    if current_admin_username and current_admin_username in users:
                        stored_password_hash = users[current_admin_username]["password"]
                        current_password_hash = hash_password(current_password)
                        
                        if stored_password_hash == current_password_hash:
                            # Update password
                            users[current_admin_username]["password"] = hash_password(new_password)
                            users[current_admin_username]["password_changed_at"] = time.time()
                            users[current_admin_username]["password_changed_by"] = current_admin_username
                            
                            # Save changes
                            save_users(users)
                            
                            st.success("Password changed successfully!")
                            st.info("Please use your new password for future logins.")
                            
                            # Update session to prevent logout
                            auth_cookie["password_changed"] = True
                            session_manager.save_session(auth_cookie)
                            
                        else:
                            st.error("Current password is incorrect. Please try again.")
                    else:
                        st.error("Admin account not found. Please contact system administrator.")
        
        st.markdown("---")
        st.markdown("### Deleted Users")
        backup_data = load_deleted_users_backup()
        
        if backup_data:
            st.write(f"**Deleted Users:** {len(backup_data)}")
            
            selected_user = st.selectbox(
                "Select user to restore:",
                list(backup_data.keys()) if backup_data else []
            )
            
            if selected_user and st.button("Restore User"):
                if restore_user_from_backup(selected_user, backup_data):
                    st.success(f"User '{selected_user}' restored successfully!")
                    st.rerun()
                else:
                    st.error(f"Failed to restore user '{selected_user}'")
        else:
            st.info("No deleted users in backup.")