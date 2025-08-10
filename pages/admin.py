import streamlit as st
import time
import json
import os
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def hash_password(password):
    """Hash password for security"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from JSON file"""
    users_file = "data/users.json"
    if os.path.exists(users_file):
        try:
            with open(users_file, 'r') as f:
                return json.load(f)
        except:
            return {"admin": {"password": hash_password("1234"), "role": "admin", "approved": True, "created_at": time.time()}}
    else:
        # Initialize with admin user
        admin_user = {"admin": {"password": hash_password("1234"), "role": "admin", "approved": True, "created_at": time.time()}}
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
            "deleted_by": "admin"  # You can enhance this to track who deleted
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

def send_approval_notification(user_data):
    """Send email notification when user is approved"""
    try:
        # Email configuration
        sender_email = "aaronmfbales@gmail.com"
        sender_password = "glby umrm cydt dlfp"
        receiver_email = user_data.get('email', '')
        
        if not receiver_email:
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = "Account Approved - CPMS"
        
        # Email body
        body = f"""
        Dear {user_data.get('first_name', '')} {user_data.get('last_name', '')},
        
        Your account has been approved by the administrator.
        
        You can now log in to the CPMS system using your credentials.
        
        Account Details:
        - Username: {user_data.get('username', '')}
        - Name: {user_data.get('first_name', '')} {user_data.get('last_name', '')}
        - Organization: {user_data.get('organization', '')}
        - Position: {user_data.get('position', '')}
        
        Please visit the login page to access the system.
        
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
        st.error(f"Failed to send approval email: {str(e)}")
        return False

def send_rejection_notification(user_data):
    """Send email notification when user is rejected"""
    try:
        # Email configuration
        sender_email = "aaronmfbales@gmail.com"
        sender_password = "glby umrm cydt dlfp"
        receiver_email = user_data.get('email', '')
        
        if not receiver_email:
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg['Subject'] = "Account Application Status - CPMS"
        
        # Email body
        body = f"""
        Dear {user_data.get('first_name', '')} {user_data.get('last_name', '')},
        
        Thank you for your interest in the CPMS system.
        
        After careful review, we regret to inform you that your account application has not been approved at this time.
        
        If you have any questions, please contact the system administrator.
        
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
        st.error(f"Failed to send rejection email: {str(e)}")
        return False

st.set_page_config(page_title="CPMS Admin", page_icon="", layout="wide")

# Load session data if it exists
def load_session():
    session_file = "session.json"
    if os.path.exists(session_file):
        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)
                return session_data
        except:
            return None
    return None

# Check if user is admin - restore session if needed
if "auth_cookie" not in st.session_state or not st.session_state["auth_cookie"]:
    # Try to restore from session file
    saved_session = load_session()
    if saved_session:
        st.session_state["authenticated"] = True
        st.session_state["auth_cookie"] = saved_session
    else:
        st.error("Access denied. Admin privileges required.")
        st.stop()

auth_cookie = st.session_state["auth_cookie"]
if auth_cookie.get("role") != "admin":
    st.error("Access denied. Admin privileges required.")
    st.stop()

# Clean and minimal CSS - no interference with toggle button
st.markdown("""
    <style>
    /* Hide Streamlit's default page navigation */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    
    /* Modern Sidebar Design */
    .stSidebar {
        background: linear-gradient(180deg, #1e3a8a 0%, #172087 100%) !important;
    }
    
    /* Make all sidebar text white */
    .stSidebar * {
        color: white !important;
    }
    
    /* Sidebar button styling */
    .stSidebar button {
        color: white !important;
        background-color: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 8px !important;
    }
    
    .stSidebar button:hover {
        background-color: rgba(255,255,255,0.2) !important;
    }
    
    /* Custom sidebar components */
    .sidebar-header {
        background: rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 24px 20px;
        margin: 30px 10px 30px 10px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .admin-logo {
        width: 50px;
        height: 50px;
        background: #60a5fa;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 8px auto 15px;
        color: white;
        font-weight: bold;
        font-size: 20px;
    }
    
    .admin-title {
        color: white;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 5px;
    }
    
    .admin-subtitle {
        color: rgba(255,255,255,0.7);
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .nav-divider {
        height: 1px;
        background: rgba(255,255,255,0.1);
        margin: 15px 20px;
    }
    
    .admin-stats {
        background: rgba(255,255,255,0.05);
        margin: 15px 10px;
        border-radius: 10px;
        padding: 12px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .admin-stats h4 {
        color: white;
        font-size: 13px;
        font-weight: 600;
        margin: 0 0 8px 0;
    }
    
    .stats-info {
        color: rgba(255,255,255,0.85);
        font-size: 11px;
        margin-bottom: 6px;
    }
    
    .user-info {
        background: rgba(255,255,255,0.1);
        border-radius: 8px;
        padding: 12px;
        border: 1px solid rgba(255,255,255,0.2);
        margin: 15px 10px;
    }
    
    .user-avatar {
        width: 35px;
        height: 35px;
        background: #60a5fa;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        margin-bottom: 8px;
    }
    
    .user-name {
        color: white;
        font-size: 13px;
        font-weight: 500;
    }
    
    .user-role {
        color: rgba(255,255,255,0.7);
        font-size: 11px;
        text-transform: capitalize;
    }
    </style>
""", unsafe_allow_html=True)

# Main content area with dynamic tabs
selected_tab = st.session_state.get("admin_selected_tab", "Pending Approvals")

# Header with selected tab name
st.markdown(f"<h1 style='color: #172087;'>Admin Dashboard - {selected_tab}</h1>", unsafe_allow_html=True)

# Display content based on selected tab
if selected_tab == "Pending Approvals":
    st.markdown("<h2>Pending User Approvals</h2>", unsafe_allow_html=True)
    
    users = load_users()
    pending_users = {username: user_data for username, user_data in users.items() 
                    if user_data.get("role") == "encoder" and not user_data.get("approved")}
    
    if not pending_users:
        st.info("No pending approvals at this time.")
    else:
        for username, user_data in pending_users.items():
            with st.expander(f"{user_data.get('first_name', '')} {user_data.get('last_name', '')} ({username})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Name:** {user_data.get('first_name', '')} {user_data.get('last_name', '')}")
                    st.write(f"**Email:** {user_data.get('email', '')}")
                    st.write(f"**Organization:** {user_data.get('organization', '')}")
                    st.write(f"**Position:** {user_data.get('position', '')}")
                    st.write(f"**Contact:** {user_data.get('contact_number', '')}")
                    st.write(f"**Registration Date:** {format_timestamp(user_data.get('created_at', 0))}")
                
                with col2:
                    col_approve, col_reject = st.columns(2)
                    with col_approve:
                        if st.button("Approve", key=f"approve_{username}"):
                            users[username]["approved"] = True
                            users[username]["approved_at"] = time.time()
                            users[username]["approved_by"] = auth_cookie.get("username", "admin")
                            save_users(users)
                            
                            # Send approval email notification
                            email_sent = send_approval_notification(user_data)
                            
                            st.success(f"User {username} approved successfully!")
                            if email_sent:
                                st.success("Approval email sent to user.")
                            else:
                                st.warning("User approved, but email notification failed.")
                            st.rerun()
                    
                    with col_reject:
                        if st.button("Reject", key=f"reject_{username}"):
                            # Send rejection email notification before deleting
                            email_sent = send_rejection_notification(user_data)
                            
                            # Remove user from users dict
                            del users[username]
                            save_users(users)
                            
                            st.success(f"User {username} rejected and removed.")
                            if email_sent:
                                st.success("Rejection email sent to user.")
                            else:
                                st.warning("User rejected, but email notification failed.")
                            st.rerun()

elif selected_tab == "All Users":
    st.markdown("<h2>All Users</h2>", unsafe_allow_html=True)
    
    users = load_users()
    
    # Create a DataFrame-like display
    st.markdown("### User List")
    
    for username, user_data in users.items():
        status = "Approved" if user_data.get("approved") else "Pending"
        role = user_data.get("role", "encoder").title()
        
        with st.expander(f"{username} - {status} ({role})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Name:** {user_data.get('first_name', '')} {user_data.get('last_name', '')}")
                st.write(f"**Email:** {user_data.get('email', '')}")
                st.write(f"**Organization:** {user_data.get('organization', '')}")
                st.write(f"**Position:** {user_data.get('position', '')}")
                st.write(f"**Contact:** {user_data.get('contact_number', '')}")
                st.write(f"**Created:** {format_timestamp(user_data.get('created_at', 0))}")
                
                if user_data.get("approved_at"):
                    st.write(f"**Approved:** {format_timestamp(user_data.get('approved_at', 0))}")
                    st.write(f"**Approved by:** {user_data.get('approved_by', 'Unknown')}")
            
            with col2:
                if user_data.get("role") != "admin":
                    # Add confirmation checkbox
                    confirm_delete = st.checkbox(f"Confirm deletion of user '{username}'", key=f"confirm_{username}")
                    
                    if st.button("Delete User", key=f"delete_{username}"):
                        if confirm_delete:
                            # Backup deleted user
                            backup_deleted_user(username, user_data)
                            # Remove user from active users
                            del users[username]
                            save_users(users)
                            st.success(f"User {username} deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Please check the confirmation box to delete this user.")

elif selected_tab == "System Settings":
    st.markdown("<h2>System Settings</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### System Information")
        users = load_users()
        total_users = len(users)
        approved_users = len([u for u in users.values() if u.get("approved")])
        pending_users = total_users - approved_users
        
        st.metric("Total Users", total_users)
        st.metric("Approved Users", approved_users)
        st.metric("Pending Approvals", pending_users)
    
    with col2:
        st.markdown("### Quick Actions")
        
        if st.button("Refresh User Data", key="settings_refresh"):
            st.rerun()
        
        if st.button("Export User Report", key="settings_export"):
            st.info("Export functionality coming soon!")
        
        if st.button("System Maintenance", key="settings_maintenance"):
            st.info("Maintenance mode coming soon!")

elif selected_tab == "Deleted Users":
    st.markdown("<h2>Deleted Users</h2>", unsafe_allow_html=True)
    
    backup_data = load_deleted_users_backup()
    
    if not backup_data:
        st.info("No deleted users found in backup.")
    else:
        st.markdown("### Deleted Users List")
        
        for username, user_data in backup_data.items():
            deleted_at = user_data.get("deleted_at", 0)
            deleted_by = user_data.get("deleted_by", "Unknown")
            
            with st.expander(f"{username} - Deleted on {format_timestamp(deleted_at)}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Name:** {user_data.get('first_name', '')} {user_data.get('last_name', '')}")
                    st.write(f"**Email:** {user_data.get('email', '')}")
                    st.write(f"**Organization:** {user_data.get('organization', '')}")
                    st.write(f"**Position:** {user_data.get('position', '')}")
                    st.write(f"**Contact:** {user_data.get('contact_number', '')}")
                    st.write(f"**Created:** {format_timestamp(user_data.get('created_at', 0))}")
                    st.write(f"**Deleted:** {format_timestamp(deleted_at)}")
                    st.write(f"**Deleted by:** {deleted_by}")
                
                with col2:
                    if st.button("Restore User", key=f"restore_{username}"):
                        if restore_user_from_backup(username, backup_data):
                            st.success(f"User {username} restored successfully!")
                            st.rerun()
                        else:
                            st.error(f"Failed to restore user {username}")

# Professional Admin Sidebar
with st.sidebar:
    # Admin header section
    st.markdown("""
        <div class="sidebar-header">
            <div class="admin-logo">A</div>
            <div class="admin-title">Admin Panel</div>
            <div class="admin-subtitle">Management Dashboard</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation section
    st.subheader("Navigation")
    
    # Initialize session state for navigation
    if "admin_selected_tab" not in st.session_state:
        st.session_state.admin_selected_tab = "Pending Approvals"
    
    # Navigation buttons
    admin_tabs = [
        "Pending Approvals",
        "All Users", 
        "System Settings",
        "Deleted Users"
    ]
    
    for tab in admin_tabs:
        if st.button(tab, key=f"nav_{tab}", use_container_width=True):
            st.session_state.admin_selected_tab = tab
            st.rerun()
    
    # Divider
    st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)
    
    # Quick actions section
    st.subheader("Quick Actions")
    
    if st.button("Refresh Data", key="refresh_data", use_container_width=True):
        st.rerun()
    
    if st.button("Export Report", key="export_report", use_container_width=True):
        st.info("Export functionality coming soon!")
    
    # System stats section
    users = load_users()
    total_users = len(users)
    approved_users = len([u for u in users.values() if u.get("approved")])
    pending_users = total_users - approved_users
    
    st.markdown(f"""
        <div class="admin-stats">
            <h4>System Overview</h4>
            <div class="stats-info">Users: {total_users}</div>
            <div class="stats-info">Active: {approved_users}</div>
            <div class="stats-info">Pending: {pending_users}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # User info section - placed right below System Overview
    auth_cookie = st.session_state["auth_cookie"]
    user_name = auth_cookie.get("first_name", auth_cookie.get("username", "Admin"))
    user_role = auth_cookie.get("role", "admin")
    
    # Safety check for user_name
    avatar_letter = user_name[0].upper() if user_name else "A"
    
    st.markdown(f"""
        <div class="user-info">
            <div class="user-avatar">{avatar_letter}</div>
            <div class="user-name">{user_name if user_name else "Admin"}</div>
            <div class="user-role">{user_role} • Active</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Add some spacing before logout button
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    if st.button("Logout", key="sidebar_logout", type="primary", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["auth_cookie"] = None
        session_file = "session.json"
        if os.path.exists(session_file):
            os.remove(session_file)
        st.switch_page("main.py") 