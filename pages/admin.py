import streamlit as st
import time
import json
import os
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from utils.admin_config import get_default_admin_user, create_admin_if_not_exists, get_admin_credentials_display
from utils.secure_session import session_manager

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

def get_user_status_indicator(status):
    """Get professional status indicator"""
    if status == 'online':
        return "●", "#22c55e"  # Green circle
    elif status == 'away':
        return "●", "#f59e0b"  # Yellow circle
    elif status == 'idle':
        return "●", "#f97316"  # Orange circle
    else:
        return "●", "#ef4444"  # Red circle

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

def send_approval_notification(user_data):
    """Send email notification when user is approved"""
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

def check_user_duplicates(username):
    """Check for duplicates in a specific user's data"""
    try:
        from utils.data_manager import data_manager
        import pandas as pd
        
        duplicate_results = {}
        
        # Define fields to check for duplicates in each sheet
        duplicate_check_fields = {
            "Client": ["First Name", "Last Name", "Full Name", "Business Name", "Email", "Contact Number"],
            "Business Owner": ["First Name", "Last Name", "Full Name", "Business Name", "Email", "Contact Number"],
            "Business Profile": ["Business Name", "Business Registration Number", "TIN", "Email"],
            "Business Registration": ["Business Name", "Registration Number", "TIN"],
            "Business Contact Information": ["Business Name", "Email", "Contact Number"],
            "Business Financial Structure": ["Business Name", "TIN"],
            "Market Domestic": ["Business Name", "Product/Service"],
            "Market Export": ["Business Name", "Product/Service", "Destination Country"],
            "Market Import": ["Business Name", "Product/Service", "Source Country"],
            "Product Service Lines": ["Business Name", "Product/Service Name"],
            "Employment Statistics": ["Business Name", "Employee Name"],
            "Assistance": ["Business Name", "Beneficiary Name"],
            "Jobs Generated": ["Business Name", "Job Title"]
        }
        
        for sheet_name, fields_to_check in duplicate_check_fields.items():
            try:
                # Load data for this sheet
                data, columns = data_manager.load_user_data(username, sheet_name)
                if not data or not columns:
                    continue
                
                df = pd.DataFrame(data, columns=columns)
                if df.empty:
                    continue
                
                sheet_duplicates = {}
                
                # Check each field for duplicates
                for field in fields_to_check:
                    if field in df.columns:
                        # Find duplicates (non-empty values only)
                        field_data = df[field].dropna()
                        field_data = field_data[field_data.astype(str).str.strip() != '']
                        
                        if len(field_data) > 1:
                            value_counts = field_data.value_counts()
                            duplicates = value_counts[value_counts > 1]
                            
                            if not duplicates.empty:
                                duplicate_list = []
                                for value, count in duplicates.items():
                                    duplicate_list.append({
                                        'value': str(value),
                                        'count': int(count)
                                    })
                                sheet_duplicates[field] = duplicate_list
                
                if sheet_duplicates:
                    duplicate_results[sheet_name] = sheet_duplicates
                    
            except Exception as e:
                continue
        
        return duplicate_results
        
    except Exception as e:
        return {}

def get_user_data_summary(username):
    """Get summary of user's data across all sheets"""
    try:
        from utils.data_manager import data_manager
        
        summary = {}
        sheet_names = [
            "Business Owner", "Business Profile", "Client", "Business Registration",
            "Business Financial Structure", "Market Import", "Product Service Lines",
            "Employment Statistics", "Assistance", "Market Export", "Jobs Generated",
            "Business Contact Information", "Market Domestic"
        ]
        
        for sheet_name in sheet_names:
            try:
                data, columns = data_manager.load_user_data(username, sheet_name)
                if data and columns:
                    summary[sheet_name] = len(data)
                else:
                    summary[sheet_name] = 0
            except:
                summary[sheet_name] = 0
        
        return summary
        
    except Exception as e:
        return {}

def check_system_wide_duplicates():
    """Check for duplicates across all users' data - like scanning an entire Excel workbook"""
    try:
        from utils.data_manager import data_manager
        import pandas as pd
        
        # Get all users
        all_users = load_users()
        regular_users = {k: v for k, v in all_users.items() if v.get("role") != "admin"}
        
        system_duplicates = {}
        
        # Define sheets and key fields to check for system-wide duplicates
        sheet_configs = {
            "Client": {
                "key_fields": ["Business Name", "Email", "Contact Number", "TIN"],
                "identity_fields": ["First Name", "Last Name", "Full Name"]
            },
            "Business Owner": {
                "key_fields": ["Business Name", "Email", "Contact Number", "TIN"],
                "identity_fields": ["First Name", "Last Name", "Full Name"]
            },
            "Business Profile": {
                "key_fields": ["Business Name", "Business Registration Number", "TIN", "Email"],
                "identity_fields": ["Business Name"]
            },
            "Business Registration": {
                "key_fields": ["Business Name", "Registration Number", "TIN"],
                "identity_fields": ["Business Name"]
            },
            "Business Contact Information": {
                "key_fields": ["Business Name", "Email", "Contact Number"],
                "identity_fields": ["Business Name"]
            }
        }
        
        for sheet_name, config in sheet_configs.items():
            # Collect all data from all users for this sheet
            all_sheet_data = []
            
            for username in regular_users.keys():
                try:
                    data, columns = data_manager.load_user_data(username, sheet_name)
                    if data and columns:
                        df = pd.DataFrame(data, columns=columns)
                        if not df.empty:
                            # Add encoder info to track who entered what
                            df['Encoder'] = username
                            all_sheet_data.append(df)
                except:
                    continue
            
            if not all_sheet_data:
                continue
                
            # Combine all users' data for this sheet
            combined_df = pd.concat(all_sheet_data, ignore_index=True)
            
            sheet_duplicates = {}
            
            # Check each key field for cross-user duplicates
            for field in config["key_fields"]:
                if field in combined_df.columns:
                    # Find duplicates across different users
                    field_data = combined_df[field].dropna()
                    field_data = field_data[field_data.astype(str).str.strip() != '']
                    
                    if len(field_data) > 1:
                        # Group by field value and check for multiple encoders
                        for value in field_data.unique():
                            matching_rows = combined_df[combined_df[field] == value]
                            encoders = matching_rows['Encoder'].unique()
                            
                            # Only flag if same value entered by different encoders OR multiple times by same encoder
                            if len(matching_rows) > 1 and (len(encoders) > 1 or len(matching_rows) > len(encoders)):
                                if field not in sheet_duplicates:
                                    sheet_duplicates[field] = []
                                
                                # Create detailed duplicate info
                                encoder_details = []
                                for encoder in encoders:
                                    encoder_rows = matching_rows[matching_rows['Encoder'] == encoder]
                                    encoder_details.append({
                                        'encoder': encoder,
                                        'count': len(encoder_rows),
                                        'rows': encoder_rows.index.tolist()
                                    })
                                
                                sheet_duplicates[field].append({
                                    'value': str(value),
                                    'total_occurrences': len(matching_rows),
                                    'encoders_involved': len(encoders),
                                    'encoder_details': encoder_details,
                                    'cross_encoder': len(encoders) > 1
                                })
            
            if sheet_duplicates:
                system_duplicates[sheet_name] = sheet_duplicates
        
        return system_duplicates
        
    except Exception as e:
        st.error(f"Error checking system-wide duplicates: {str(e)}")
        return {}

st.set_page_config(page_title="CPMS Admin", page_icon="", layout="wide")

# Admin page session restoration - make it completely self-sufficient
print(f"Admin page load - auth_cookie in session_state: {'auth_cookie' in st.session_state}")

# Always try to restore session if not authenticated
if "authenticated" not in st.session_state or not st.session_state.get("authenticated"):
    print("Session not authenticated, attempting restoration...")
    try:
        # Debug browser ID and session file
        browser_id = session_manager.get_browser_id()
        session_file = session_manager.get_session_file_path()
        print(f"Browser ID: {browser_id}")
        print(f"Session file path: {session_file}")
        print(f"Session file exists: {os.path.exists(session_file)}")
        
        saved_session = session_manager.load_session()
        print(f"Saved session found: {saved_session is not None}")
        if saved_session:
            print(f"Saved session data: {saved_session}")
            
        if saved_session and saved_session.get("authenticated") and saved_session.get("role") == "admin":
            st.session_state["authenticated"] = True
            st.session_state["auth_cookie"] = saved_session
            print("Admin session restored successfully")
        else:
            print("No valid admin session found")
            st.error("Access denied. Admin privileges required.")
            st.markdown("[← Go back to login page](../)")
            st.stop()
    except Exception as e:
        print(f"Admin session restore error: {e}")
        st.error("Access denied. Admin privileges required.")
        st.markdown("[← Go back to login page](../)")
        st.stop()

# Double-check admin role
auth_cookie = st.session_state.get("auth_cookie")
if not auth_cookie or auth_cookie.get("role") != "admin":
    print(f"Admin role verification failed. Role: {auth_cookie.get('role') if auth_cookie else 'None'}")
    st.error("Access denied. Admin privileges required.")
    st.markdown("[← Go back to login page](../)")
    st.stop()

print("Admin access verified successfully")

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
    
    /* Sidebar button styling with white outline */
    .stSidebar button {
        color: white !important;
        background-color: rgba(255,255,255,0.1) !important;
        border: 2px solid #fff !important;
        border-radius: 8px !important;
        box-shadow: 0 0 0 2px rgba(255,255,255,0.15) !important;
        transition: border 0.2s, box-shadow 0.2s;
    }
    .stSidebar button:hover {
        background-color: rgba(255,255,255,0.2) !important;
        border: 2.5px solid #fff !important;
        box-shadow: 0 0 0 3px rgba(255,255,255,0.25) !important;
    }
    
    /* Active Users Status Cards */
    .user-status-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
        transition: all 0.2s ease;
    }
    
    .user-status-card:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transform: translateY(-1px);
    }
    
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-weight: 600;
        font-size: 14px;
    }
    
    .status-online {
        color: #22c55e;
    }
    
    .status-away {
        color: #f59e0b;
    }
    
    .status-idle {
        color: #f97316;
    }
    
    .user-info-grid {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr 1fr;
        gap: 16px;
        align-items: center;
        padding: 12px 0;
    }
    
    .activity-metrics {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
        border: 1px solid #bae6fd;
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
    
    /* Hide Streamlit's "Hosted with Streamlit" badge and promotional content */
    .stAppDeployButton,
    div[data-testid="stAppDeployButton"],
    a[href*="streamlit.io"],
    div:contains("Hosted with Streamlit"),
    [data-testid="stBottom"],
    .st-emotion-cache-h4xjwg,
    div[class*="floating"],
    div[class*="badge"],
    .stAppViewBlockContainer > div:last-child:contains("Streamlit") {
        display: none !important;
    }
    
    /* Hide any footer elements */
    footer, .stAppViewContainer footer {
        display: none !important;
    }
    
    /* DTI Blue Button Styling */
    .dti-blue-button {
        background-color: #172087 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 4px rgba(23, 32, 135, 0.2) !important;
    }
    
    .dti-blue-button:hover {
        background-color: #1e3a8a !important;
        box-shadow: 0 4px 8px rgba(23, 32, 135, 0.3) !important;
        transform: translateY(-1px) !important;
    }
    
    .dti-blue-button:active {
        background-color: #1d4ed8 !important;
        transform: translateY(0) !important;
    }
    
    /* Target specific button by its content */
    button[kind="primary"]:has-text("Scan All User Data for Duplicates"),
    button:contains("Scan All User Data for Duplicates") {
        background-color: #172087 !important;
        border-color: #172087 !important;
        color: white !important;
    }
    
    button[kind="primary"]:has-text("Scan All User Data for Duplicates"):hover,
    button:contains("Scan All User Data for Duplicates"):hover {
        background-color: #1e3a8a !important;
        border-color: #1e3a8a !important;
        box-shadow: 0 4px 8px rgba(23, 32, 135, 0.3) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize admin navigation state - restore from session only on first load
if "admin_selected_tab" not in st.session_state:
    # First load - try to restore from session
    if auth_cookie and 'current_admin_tab' in auth_cookie:
        st.session_state["admin_selected_tab"] = auth_cookie['current_admin_tab']
    else:
        st.session_state["admin_selected_tab"] = "Pending Approvals"

selected_tab = st.session_state.get("admin_selected_tab", "Pending Approvals")

# Update admin session activity and preserve current tab
try:
    current_tab = st.session_state.get("admin_selected_tab", "Pending Approvals") 
    auth_cookie['current_admin_tab'] = current_tab
    session_manager.save_session(auth_cookie)
except Exception as e:
    print(f"Admin session update error: {e}")

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

elif selected_tab == "Active Users":
    st.markdown("<h2>Active Users Online</h2>", unsafe_allow_html=True)
    
    # Get active users data
    active_users = get_active_users()
    
    # Auto-refresh functionality
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"**Total Active Users:** {len(active_users)}")
    with col2:
        auto_refresh = st.checkbox("Auto-refresh (30s)", value=False, key="auto_refresh_users")
    with col3:
        if st.button("⟳ Refresh Now", key="manual_refresh_users"):
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
        # Professional status cards layout
        st.markdown("### Current Active Sessions")
        
        # Group users by status for better organization
        online_users = [u for u in active_users if u['status'] == 'online']
        away_users = [u for u in active_users if u['status'] == 'away']
        idle_users = [u for u in active_users if u['status'] == 'idle']
        
        # Status summary tabs
        tab1, tab2, tab3 = st.tabs([
            f"● Online ({len(online_users)})",
            f"● Away ({len(away_users)})", 
            f"● Idle ({len(idle_users)})"
        ])
        
        with tab1:
            if online_users:
                for user in online_users:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                        
                        with col1:
                            st.markdown(f"**{user['full_name']}** (`{user['username']}`)")
                            st.caption(f"Role: {user['role'].title()}")
                        
                        with col2:
                            st.markdown('<span style="color: #22c55e;">● **Online**</span>', unsafe_allow_html=True)
                            st.caption("Active now")
                        
                        with col3:
                            st.markdown(f"**Last Activity:**")
                            st.caption(format_time_ago(user['last_activity']))
                        
                        with col4:
                            st.markdown(f"**Session Started:**")
                            session_start = user.get('session_start', 'unknown')
                            if session_start != 'unknown':
                                try:
                                    start_time = datetime.fromisoformat(session_start)
                                    st.caption(start_time.strftime('%H:%M'))
                                except:
                                    st.caption("Unknown")
                            else:
                                st.caption("Unknown")
                        
                        st.markdown("---")
            else:
                st.info("No users currently online.")
        
        with tab2:
            if away_users:
                for user in away_users:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                        
                        with col1:
                            st.markdown(f"**{user['full_name']}** (`{user['username']}`)")
                            st.caption(f"Role: {user['role'].title()}")
                        
                        with col2:
                            st.markdown('<span style="color: #f59e0b;">● **Away**</span>', unsafe_allow_html=True)
                            st.caption("Recently active")
                        
                        with col3:
                            st.markdown(f"**Last Activity:**")
                            st.caption(format_time_ago(user['last_activity']))
                        
                        with col4:
                            st.markdown(f"**Session Started:**")
                            session_start = user.get('session_start', 'unknown')
                            if session_start != 'unknown':
                                try:
                                    start_time = datetime.fromisoformat(session_start)
                                    st.caption(start_time.strftime('%H:%M'))
                                except:
                                    st.caption("Unknown")
                            else:
                                st.caption("Unknown")
                        
                        st.markdown("---")
            else:
                st.info("No users currently away.")
        
        with tab3:
            if idle_users:
                for user in idle_users:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                        
                        with col1:
                            st.markdown(f"**{user['full_name']}** (`{user['username']}`)")
                            st.caption(f"Role: {user['role'].title()}")
                        
                        with col2:
                            st.markdown('<span style="color: #f97316;">● **Idle**</span>', unsafe_allow_html=True)
                            st.caption("Inactive")
                        
                        with col3:
                            st.markdown(f"**Last Activity:**")
                            st.caption(format_time_ago(user['last_activity']))
                        
                        with col4:
                            st.markdown(f"**Session Started:**")
                            session_start = user.get('session_start', 'unknown')
                            if session_start != 'unknown':
                                try:
                                    start_time = datetime.fromisoformat(session_start)
                                    st.caption(start_time.strftime('%H:%M'))
                                except:
                                    st.caption("Unknown")
                            else:
                                st.caption("Unknown")
                        
                        st.markdown("---")
            else:
                st.info("No users currently idle.")
        
        # Activity metrics
        st.markdown("---")
        st.markdown("### Activity Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Active", len(active_users))
        with col2:
            st.metric("Online Now", len(online_users), delta=f"{len(online_users)}")
        with col3:
            st.metric("Away", len(away_users), delta=f"{len(away_users)}")
        with col4:
            st.metric("Idle", len(idle_users), delta=f"{len(idle_users)}")

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

elif selected_tab == "User Data Management":
    st.markdown("<h2>User Data Management</h2>", unsafe_allow_html=True)
    
    # Get all users
    all_users = load_users()
    regular_users = {k: v for k, v in all_users.items() if v.get("role") != "admin"}
    
    if regular_users:
        st.markdown(f"### {len(regular_users)} Registered Users")
        
        # Check for user data files
        from utils.data_manager import data_manager
        
        for username, user_data in regular_users.items():
            user_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
            display_name = user_name if user_name else username
            
            # Check if user has data
            has_data = data_manager.user_has_data(username)
            status_icon = "[DATA]" if has_data else "[EMPTY]"
            status_text = "Has Data" if has_data else "No Data"
            
            # Create expandable section for each user
            with st.expander(f"{status_icon} {display_name} ({username}) - {status_text}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Email:** {user_data.get('email', 'N/A')}")
                    st.write(f"**Status:** {'Approved' if user_data.get('approved') else 'Pending'}")
                
                with col2:
                    if has_data:
                        # Button to check duplicates for this user
                        if st.button(f"Check Duplicates", key=f"check_dupes_{username}", use_container_width=True):
                            st.session_state[f"show_duplicates_{username}"] = True
                            st.rerun()
                        
                        # Button to view data summary
                        if st.button(f"View Data Summary", key=f"view_summary_{username}", use_container_width=True):
                            st.session_state[f"show_summary_{username}"] = True
                            st.rerun()
                
                # Show duplicates if requested
                if st.session_state.get(f"show_duplicates_{username}", False):
                    st.markdown("**Duplicate Check Results:**")
                    duplicates = check_user_duplicates(username)
                    
                    if duplicates:
                        for sheet_name, sheet_duplicates in duplicates.items():
                            if sheet_duplicates:
                                st.warning(f"**{sheet_name}:**")
                                for field, duplicate_list in sheet_duplicates.items():
                                    if duplicate_list:
                                        st.write(f"• **{field}:** {len(duplicate_list)} duplicate(s)")
                                        for dup in duplicate_list:
                                            st.write(f"  - '{dup['value']}' appears {dup['count']} times")
                    else:
                        st.success("No duplicates found!")
                    
                    if st.button(f"Close Results", key=f"close_dupes_{username}"):
                        st.session_state[f"show_duplicates_{username}"] = False
                        st.rerun()
                
                # Show data summary if requested
                if st.session_state.get(f"show_summary_{username}", False):
                    st.markdown("**Data Summary:**")
                    summary = get_user_data_summary(username)
                    
                    if summary:
                        for sheet_name, count in summary.items():
                            if count > 0:
                                st.write(f"• **{sheet_name}:** {count} records")
                    else:
                        st.info("No data found")
                    
                    if st.button(f"Close Summary", key=f"close_summary_{username}"):
                        st.session_state[f"show_summary_{username}"] = False
                        st.rerun()
    else:
        st.info("No regular users registered yet")

elif selected_tab == "System Data Analysis":
    st.markdown("<h2>System Data Analysis</h2>", unsafe_allow_html=True)
    st.markdown("*Comprehensive data scanning across all users - like analyzing an entire Excel workbook*")
    
    # System-wide duplicate detection
    st.markdown("### System-Wide Duplicate Detection")
    st.info("This tool scans ALL user data to find identical entries across different encoders, helping identify data redundancy and potential coordination issues.")
    
    # Add custom CSS for this specific button
    st.markdown("""
        <style>
        div[data-testid="stButton"] > button:first-child {
            background-color: #172087 !important;
            border-color: #172087 !important;
            color: white !important;
        }
        div[data-testid="stButton"] > button:first-child:hover {
            background-color: #1e3a8a !important;
            border-color: #1e3a8a !important;
            box-shadow: 0 4px 8px rgba(23, 32, 135, 0.3) !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    if st.button("Scan All User Data for Duplicates", type="primary", use_container_width=True, key="dti_scan_button"):
        with st.spinner("Scanning all user data... This may take a moment."):
            system_duplicates = check_system_wide_duplicates()
        
        if system_duplicates:
            st.markdown("### System-Wide Duplicates Found")
            
            for sheet_name, sheet_duplicates in system_duplicates.items():
                st.markdown(f"#### {sheet_name} Sheet")
                
                for field, duplicates in sheet_duplicates.items():
                    st.markdown(f"**{field} Duplicates:**")
                    
                    for dup_info in duplicates:
                        value = dup_info['value']
                        total = dup_info['total_occurrences']
                        encoder_count = dup_info['encoders_involved']
                        is_cross_encoder = dup_info['cross_encoder']
                        
                        # Color code based on severity
                        if is_cross_encoder:
                            st.error(f"**CRITICAL**: '{value}' - {total} occurrences across {encoder_count} different encoders")
                        else:
                            st.warning(f"**WARNING**: '{value}' - {total} duplicate entries by same encoder")
                        
                        # Show encoder details
                        for encoder_detail in dup_info['encoder_details']:
                            encoder = encoder_detail['encoder']
                            count = encoder_detail['count']
                            st.write(f"   • **{encoder}**: {count} entries")
                        
                        st.write("")  # Add spacing
        else:
            st.success("**No system-wide duplicates found!** All data appears to be unique across all users.")
    
    st.markdown("---")
    
    # Data distribution analysis
    st.markdown("### Data Distribution Analysis")
    
    if st.button("Analyze Data Distribution", type="secondary", use_container_width=True):
        st.markdown("#### User Data Volume Analysis")
        
        # Get all users and their data counts
        all_users = load_users()
        regular_users = {k: v for k, v in all_users.items() if v.get("role") != "admin"}
        
        from utils.data_manager import data_manager
        
        user_data_summary = {}
        total_records = 0
        
        for username in regular_users.keys():
            user_summary = get_user_data_summary(username)
            user_total = sum(user_summary.values())
            user_data_summary[username] = {
                'total_records': user_total,
                'sheet_breakdown': user_summary
            }
            total_records += user_total
        
        # Display summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total System Records", total_records)
        with col2:
            st.metric("Active Data Users", len([u for u in user_data_summary.values() if u['total_records'] > 0]))
        with col3:
            st.metric("Empty Users", len([u for u in user_data_summary.values() if u['total_records'] == 0]))
        with col4:
            avg_records = total_records / len(regular_users) if regular_users else 0
            st.metric("Avg Records/User", f"{avg_records:.1f}")
        
        # Show per-user breakdown
        st.markdown("#### Per-User Data Breakdown")
        
        # Sort users by total records (descending)
        sorted_users = sorted(user_data_summary.items(), key=lambda x: x[1]['total_records'], reverse=True)
        
        for username, data_info in sorted_users:
            user_data = regular_users[username]
            user_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
            display_name = user_name if user_name else username
            
            total = data_info['total_records']
            
            if total > 0:
                with st.expander(f"[DATA] {display_name} ({username}) - {total} total records"):
                    # Show sheet breakdown
                    sheet_data = data_info['sheet_breakdown']
                    active_sheets = {k: v for k, v in sheet_data.items() if v > 0}
                    
                    if active_sheets:
                        cols = st.columns(min(3, len(active_sheets)))
                        for i, (sheet, count) in enumerate(active_sheets.items()):
                            with cols[i % 3]:
                                st.metric(sheet, count)
            else:
                st.info(f"[EMPTY] {display_name} ({username}) - No data entered")

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
    
    # Navigation buttons
    admin_tabs = [
        "Pending Approvals",
        "Active Users",
        "All Users",
        "User Data Management",
        "System Data Analysis", 
        "System Settings",
        "Deleted Users"
    ]
    
    for tab in admin_tabs:
        if st.button(tab, key=f"nav_{tab}", use_container_width=True):
            st.session_state.admin_selected_tab = tab
            st.rerun()
    
    # Divider
    st.markdown('<div class="nav-divider"></div>', unsafe_allow_html=True)
    
    # System stats section
    users = load_users()
    active_users = get_active_users()
    total_users = len(users)
    approved_users = len([u for u in users.values() if u.get("approved")])
    pending_users = total_users - approved_users
    online_count = len([u for u in active_users if u['status'] == 'online'])
    
    st.markdown(f"""
        <div class="admin-stats">
            <h4>System Overview</h4>
            <div class="stats-info">Users: {total_users}</div>
            <div class="stats-info">Active: {approved_users}</div>
            <div class="stats-info">Online: {online_count}</div>
            <div class="stats-info">Pending: {pending_users}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Admin Configuration Info
    st.markdown("---")
    st.markdown("### Admin Configuration")
    
    admin_info = get_admin_credentials_display()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Username:** `{admin_info['username']}`")
        st.markdown(f"**Email:** `{admin_info['email']}`")
    with col2:
        st.markdown(f"**Name:** {admin_info['name']}")
        st.markdown(f"**Password:** {admin_info['password']}")
    
    st.info("Admin credentials are stored securely in Streamlit secrets")
    
    if st.button("Reset Admin Account", help="This will recreate the admin account with current settings"):
        try:
            # Remove existing admin and recreate
            users = load_users()
            # Find and remove any existing admin accounts
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
    
    st.markdown("---")
    
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
    # Custom styled Logout button for better visibility
    logout_btn_css = """
    <style>
    .dti-logout-btn {
        background-color: #172087 !important;
        color: #fff !important;
        border: 2.5px solid #fff !important;
        border-radius: 8px !important;
        padding: 16px 0 !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        width: 100% !important;
        margin-top: 10px !important;
        margin-bottom: 10px !important;
        box-shadow: 0 2px 8px rgba(23,32,135,0.15) !important;
        transition: background 0.2s, box-shadow 0.2s, border 0.2s;
    }
    .dti-logout-btn:hover {
        background-color: #1e3a8a !important;
        box-shadow: 0 4px 16px rgba(23,32,135,0.25) !important;
        border: 3px solid #fff !important;
    }
    </style>
    """
    st.markdown(logout_btn_css, unsafe_allow_html=True)
    if st.button("Logout", key="sidebar_logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["auth_cookie"] = None
        # Clear browser-specific session
        session_manager.clear_session()
        st.switch_page("main.py")
    # Add custom class to the button using JavaScript
    st.markdown("""
    <script>
    const logoutBtn = window.parent.document.querySelector('button[data-testid="sidebar_logout"]');
    if (logoutBtn) { logoutBtn.classList.add('dti-logout-btn'); }
    </script>
    """, unsafe_allow_html=True)