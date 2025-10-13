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

def generate_secure_password(length=12):
    """Generate a secure random password"""
    characters = string.ascii_letters + string.digits + "!@#$%&*"
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def send_account_creation_email(user_data, password):
    """Send email with account credentials to new encoder"""
    try:
        # Email configuration - using Streamlit secrets
        sender_email = st.secrets.get("email", {}).get("sender_email", "aaronmfbales@gmail.com")
        sender_password = st.secrets.get("email", {}).get("sender_password", "")
        receiver_email = user_data.get('email', '')
        
        if not receiver_email:
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = "CPMS Account Created - Login Credentials"
        
        # Email body
        body = f"""
        Dear {user_data.get('first_name', '')} {user_data.get('last_name', '')},
        
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
        CPMS Administration Team
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
        st.error(f"Failed to send account creation email: {str(e)}")
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
    
    /* Ensure our custom navigation is at the top */
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
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

# Header section
st.markdown("""
    <div style="background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); padding: 2rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0; text-align: center; font-size: 2.5rem; font-weight: bold;">
            MSME CPMS ADMIN DASHBOARD
        </h1>
        <p style="color: #bfdbfe; margin: 0.5rem 0 0 0; text-align: center; font-size: 1.1rem;">
            Client Profile Management System - Administrative Control Panel
        </p>
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
    st.markdown("## Navigation")
    
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
    
    st.markdown("## Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Encoders", total_encoders)
        st.metric("Online Now", online_count)
    with col2:
        st.metric("Admin Sessions", 1)
        st.metric("System Status", "Active")
    
    st.divider()
    
    # Admin Info
    admin_name = f"{auth_cookie.get('first_name', 'Admin')} {auth_cookie.get('last_name', '')}"
    st.markdown("## Admin Info")
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
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name *", help="Encoder's first name")
            last_name = st.text_input("Last Name *", help="Encoder's last name")
            email = st.text_input("Email Address *", help="Valid email address for sending credentials")
            
        with col2:
            username = st.text_input("Username *", help="Unique username for login")
            organization = st.text_input("Organization/Department", help="Organization or department")
            position = st.text_input("Position/Title", help="Job position or title")
        
        contact_number = st.text_input("Contact Number", help="Phone number (optional)")
        
        st.markdown("### Password Options")
        password_option = st.radio(
            "Choose password method:",
            ["Generate secure password automatically", "Set custom password"],
            help="Automatically generated passwords are more secure"
        )
        
        custom_password = ""
        if password_option == "Set custom password":
            custom_password = st.text_input("Custom Password", type="password", help="Minimum 8 characters")
            confirm_password = st.text_input("Confirm Password", type="password")
        
        st.markdown("### Email Notification")
        send_email = st.checkbox("Send credentials via email", value=True, help="Email the login credentials to the encoder")
        
        submitted = st.form_submit_button("Create Encoder Account", type="primary", use_container_width=True)
        
        if submitted:
            # Validation
            errors = []
            
            if not all([first_name, last_name, email, username]):
                errors.append("All required fields (*) must be filled")
            
            if password_option == "Set custom password":
                if len(custom_password) < 8:
                    errors.append("Custom password must be at least 8 characters")
                if custom_password != confirm_password:
                    errors.append("Passwords do not match")
            
            # Check if username or email already exists
            existing_users = load_users()
            if username in existing_users:
                errors.append("Username already exists")
            
            for user_data in existing_users.values():
                if user_data.get("email") == email:
                    errors.append("Email already registered")
                    break
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Generate or use custom password
                if password_option == "Generate secure password automatically":
                    password = generate_secure_password()
                else:
                    password = custom_password
                
                # Create new encoder account
                new_encoder = {
                    "password": hash_password(password),
                    "role": "encoder",
                    "approved": True,  # Auto-approved since created by admin
                    "created_at": time.time(),
                    "created_by": auth_cookie.get("username", "admin"),
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "organization": organization,
                    "position": position,
                    "contact_number": contact_number
                }
                
                # Save to users database
                existing_users[username] = new_encoder
                save_users(existing_users)
                
                # Success message
                st.success(f"Encoder account '{username}' created successfully!")
                
                # Show credentials
                st.info(f"**Login Credentials:**\n- Username: `{username}`\n- Password: `{password}`")
                
                # Send email if requested
                if send_email:
                    with st.spinner("Sending credentials via email..."):
                        email_sent = send_account_creation_email(new_encoder, password)
                    
                    if email_sent:
                        st.success("Credentials sent via email successfully!")
                    else:
                        st.error("Failed to send email. Please share credentials manually.")
                
                st.markdown("---")
                st.markdown("**Next Steps:**")
                st.markdown("1. Account is ready to use immediately")
                st.markdown("2. Encoder will receive login credentials via email")
                st.markdown("3. Encoder should change password after first login")
                st.markdown("4. Encoder can start entering data into CPMS")

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
                    
                    # Reset Password
                    if st.button("Reset Password", key=f"reset_pwd_{username}"):
                        new_password = generate_secure_password()
                        users[username]["password"] = hash_password(new_password)
                        save_users(users)
                        
                        st.success(f"Password reset successfully!")
                        st.info(f"New password: `{new_password}`")
                        
                        # Optionally send email
                        if st.button("Email New Password", key=f"email_pwd_{username}"):
                            email_sent = send_account_creation_email(user_data, new_password)
                            if email_sent:
                                st.success("Password sent via email!")
                            else:
                                st.error("Failed to send email")
                    
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
                    Online • {user['role'].title()} • Last activity: {format_time_ago(user['last_activity'])}
                    """)
                    st.divider()
            else:
                st.info("No users currently online.")
        
        with tab2:
            if away_users:
                for user in away_users:
                    st.markdown(f"""
                    **{user['full_name']}** (`{user['username']}`)  
                    Away • {user['role'].title()} • Last activity: {format_time_ago(user['last_activity'])}
                    """)
                    st.divider()
            else:
                st.info("No users currently away.")
        
        with tab3:
            if idle_users:
                for user in idle_users:
                    st.markdown(f"""
                    **{user['full_name']}** (`{user['username']}`)  
                    Idle • {user['role'].title()} • Last activity: {format_time_ago(user['last_activity'])}
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
        
        if st.button("Reset Admin Account", help="Recreate admin account with current settings"):
            try:
                # Remove existing admin and recreate
                users = load_users()
                admin_keys_to_remove = [k for k, v in users.items() if v.get("role") == "admin"]
                for key in admin_keys_to_remove:
                    del users[key]
                
                # Add new admin
                created, message = create_admin_if_not_exists(users)
                if created:
                    save_users(users)
                    st.success("Admin account reset successfully!")
                    st.rerun()
                else:
                    st.warning("Could not reset admin account")
            except Exception as e:
                st.error(f"Error resetting admin account: {str(e)}")
        
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