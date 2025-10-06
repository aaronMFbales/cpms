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
        # Email configuration - using Streamlit secrets (match secrets.toml keys)
        sender_email = st.secrets.get("email", {}).get("username", "aaronmfbales@gmail.com")
        sender_password = st.secrets.get("email", {}).get("password", "")
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
        # Email configuration - using Streamlit secrets (match secrets.toml keys)
        sender_email = st.secrets.get("email", {}).get("username", "aaronmfbales@gmail.com")
        sender_password = st.secrets.get("email", {}).get("password", "")
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

st.set_page_config(page_title="MSME CPMS Admin Dashboard", page_icon="", layout="wide")

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

# Modern Professional Admin Dashboard CSS
st.markdown("""
    <style>
    /* Global Styles */
    .stApp {
        background: #f8fafc;
    }
    
    /* Hide Streamlit's default elements */
    [data-testid="stSidebarNav"],
    .stSidebar,
    #MainMenu,
    footer,
    .stAppDeployButton,
    div[data-testid="stAppDeployButton"],
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    /* Dashboard Header */
    .admin-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #172087 50%, #1e40af 100%);
        color: white;
        padding: 2rem 3rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 8px 32px rgba(23, 32, 135, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .admin-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
        opacity: 0.3;
    }
    
    .admin-header-content {
        position: relative;
        z-index: 1;
    }
    
    .admin-title {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        letter-spacing: 1px;
    }
    
    .admin-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        font-weight: 400;
    }
    
    /* Navigation Menu */
    .nav-container {
        padding: 0.5rem 0;
        margin-bottom: 1rem;
    }
    
    .nav-menu {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        justify-content: center;
        align-items: center;
    }
    
    .nav-item {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-align: center;
        min-width: 180px;
        position: relative;
        overflow: hidden;
    }
    
    .nav-item:hover {
        background: linear-gradient(135deg, #172087 0%, #1e40af 100%);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(23, 32, 135, 0.25);
        border-color: #172087;
    }
    
    .nav-item.active {
        background: linear-gradient(135deg, #172087 0%, #1e40af 100%);
        color: white;
        border-color: #172087;
        box-shadow: 0 4px 15px rgba(23, 32, 135, 0.3);
    }
    
    .nav-item-title {
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0;
    }
    
    .nav-item-desc {
        font-size: 0.75rem;
        opacity: 0.8;
        margin-top: 0.25rem;
    }
    
    /* Content Area */
    .content-area {
        padding: 0;
        margin-top: 0;
    }
    
    .content-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #f1f5f9;
    }
    
    .content-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #172087;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .content-badge {
        background: linear-gradient(135deg, #172087 0%, #1e40af 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Professional Tables */
    .data-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
        background: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .data-table th {
        background: linear-gradient(135deg, #172087 0%, #1e40af 100%);
        color: white;
        padding: 1rem;
        text-align: left;
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .data-table td {
        padding: 1rem;
        border-bottom: 1px solid #f1f5f9;
        vertical-align: top;
    }
    
    .data-table tr:hover {
        background: #f8fafc;
    }
    
    .data-table tr:last-child td {
        border-bottom: none;
    }
    
    /* Status Indicators */
    .status-online {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        color: #059669;
        font-weight: 600;
    }
    
    .status-away {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        color: #d97706;
        font-weight: 600;
    }
    
    .status-idle {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        color: #dc2626;
        font-weight: 600;
    }
    
    .status-pending {
        background: #fef3c7;
        color: #92400e;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .status-approved {
        background: #d1fae5;
        color: #065f46;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* Action Buttons */
    .action-btn {
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        font-weight: 600;
        font-size: 0.8rem;
        transition: all 0.2s ease;
        margin: 0.25rem;
    }
    
    .btn-approve {
        background: #059669;
        color: white;
    }
    
    .btn-approve:hover {
        background: #047857;
        transform: translateY(-1px);
    }
    
    .btn-reject {
        background: #dc2626;
        color: white;
    }
    
    .btn-reject:hover {
        background: #b91c1c;
        transform: translateY(-1px);
    }
    
    .btn-secondary {
        background: #6b7280;
        color: white;
    }
    
    .btn-secondary:hover {
        background: #4b5563;
        transform: translateY(-1px);
    }
    
    /* Metrics Cards */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        text-align: center;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #172087;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6b7280;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.5rem;
    }
    
    /* Empty States */
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: #6b7280;
    }
    
    .empty-state-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
        opacity: 0.5;
    }
    
    /* Admin Info Panel */
    .admin-info-panel {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 1px solid #bae6fd;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.25rem 0 1rem 0;
    }
    
    .admin-info-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
    }
    
    .admin-info-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .admin-info-label {
        font-weight: 600;
        color: #0c4a6e;
        min-width: 80px;
    }
    
    /* Data Tables */
    .data-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        background: white;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .data-table th {
        background: linear-gradient(135deg, #172087 0%, #1e3a8a 100%);
        color: white;
        padding: 15px 12px;
        text-align: left;
        font-weight: 600;
        font-size: 14px;
        border: none;
    }
    
    .data-table td {
        padding: 12px;
        border-bottom: 1px solid #e5e7eb;
        vertical-align: top;
        font-size: 13px;
        line-height: 1.4;
    }
    
    .data-table tr:hover {
        background-color: #f9fafb;
    }
    
    .data-table tr:last-child td {
        border-bottom: none;
    }
    
    .status-approved {
        background: #dcfce7;
        color: #166534;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
    }
    
    .status-pending {
        background: #fef3c7;
        color: #92400e;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
    }
    
    .status-online {
        background: #dcfce7;
        color: #166534;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
    }
    
    .status-offline {
        background: #f3f4f6;
        color: #374151;
        padding: 4px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
    }
    
    .admin-info-value {
        color: #0369a1;
        font-family: 'Courier New', monospace;
        background: rgba(255,255,255,0.7);
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .nav-menu {
            flex-direction: column;
        }
        
        .nav-item {
            min-width: 100%;
        }
        
        .content-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 1rem;
        }
        
        .metrics-grid {
            grid-template-columns: 1fr;
        }
    }
    
    /* Hide Streamlit default styling */
    .stButton > button {
        display: none;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #172087;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #1e40af;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize admin navigation state
if "admin_selected_tab" not in st.session_state:
    st.session_state["admin_selected_tab"] = "Dashboard Overview"

# Available admin sections
admin_sections = [
    {
        "id": "dashboard_overview",
        "title": "Dashboard Overview",
        "description": "System metrics & analytics",
        "icon": ""
    },
    {
        "id": "pending_approvals", 
        "title": "Pending Approvals",
        "description": "Review user registrations",
        "icon": ""
    },
    {
        "id": "active_users",
        "title": "Active Users", 
        "description": "Monitor online activity",
        "icon": ""
    },
    {
        "id": "all_users",
        "title": "All Users",
        "description": "Manage user accounts",
        "icon": ""
    },
    {
        "id": "user_data_management",
        "title": "User Data Management",
        "description": "Data analysis & reports",
        "icon": ""
    },
    {
        "id": "system_data_analysis",
        "title": "System Data Analysis",
        "description": "System-wide insights",
        "icon": ""
    },
    {
        "id": "system_settings",
        "title": "System Settings",
        "description": "Configuration & settings",
        "icon": ""
    },
    {
        "id": "deleted_users",
        "title": "Deleted Users",
        "description": "Restore deleted accounts",
        "icon": ""
    }
]

# Update admin session activity
try:
    current_tab = st.session_state.get("admin_selected_tab", "Dashboard Overview")
    auth_cookie['current_admin_tab'] = current_tab
    session_manager.save_session(auth_cookie)
except Exception as e:
    print(f"Admin session update error: {e}")

# Clean integrated header with dropdown menu
st.markdown("""
<div style="position: fixed; top: 0; left: 0; right: 0; height: 50px; background: linear-gradient(90deg, #172087 0%, #1e3a8a 50%, #172087 100%); z-index: 1001; display: flex; align-items: center; justify-content: space-between; padding: 0 2rem;">
    <div style="color: white; font-size: 18px; font-weight: 800; text-shadow: 1px 1px 0px rgba(0,0,0,0.6), 2px 2px 0px rgba(0,0,0,0.4), 3px 3px 0px rgba(0,0,0,0.2), 4px 4px 10px rgba(0,0,0,0.2); transform: perspective(500px) rotateX(15deg); filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.3));">
        MSME CPMS ADMIN DASHBOARD
    </div>
    <div style="position: relative;">
        <div id="dropdown-trigger" style="background: rgba(255,255,255,0.15); backdrop-filter: blur(10px); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.2); cursor: pointer; transition: all 0.3s ease; display: flex; align-items: center; gap: 8px; color: white; font-size: 14px; font-weight: 500;" title="User Menu">
            Admin
            <svg id="dropdown-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" style="transition: transform 0.3s ease;">
                <path d="M7 10L12 15L17 10" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <div id="dropdown-menu" style="position: absolute; top: 45px; right: 0; background: rgba(255,255,255,0.95); backdrop-filter: blur(15px); border-radius: 8px; border: 1px solid rgba(255,255,255,0.3); box-shadow: 0 8px 32px rgba(0,0,0,0.3); min-width: 150px; opacity: 0; visibility: hidden; transform: translateY(-10px); transition: all 0.3s ease; z-index: 1002;">
            <div id="user-profile-item" style="padding: 12px 16px; cursor: pointer; transition: background 0.2s ease; border-bottom: 1px solid rgba(0,0,0,0.1); color: #172087; font-weight: 500; display: flex; align-items: center; gap: 8px;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="#172087" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <circle cx="12" cy="7" r="4" stroke="#172087" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                User Profile
            </div>
            <div id="logout-item" style="padding: 12px 16px; cursor: pointer; transition: background 0.2s ease; color: #dc2626; font-weight: 500; display: flex; align-items: center; gap: 8px;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M9 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H9" stroke="#dc2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <polyline points="16,17 21,12 16,7" stroke="#dc2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <line x1="21" y1="12" x2="9" y2="12" stroke="#dc2626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Logout
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# JavaScript for dropdown functionality
st.components.v1.html("""
<script>
let dropdownOpen = false;

function toggleDropdown() {
    const menu = parent.document.getElementById('dropdown-menu');
    const arrow = parent.document.getElementById('dropdown-arrow');
    const trigger = parent.document.getElementById('dropdown-trigger');
    
    if (!menu || !arrow || !trigger) return;
    
    dropdownOpen = !dropdownOpen;
    
    if (dropdownOpen) {
        menu.style.opacity = '1';
        menu.style.visibility = 'visible';
        menu.style.transform = 'translateY(0)';
        arrow.style.transform = 'rotate(180deg)';
        trigger.style.background = 'rgba(255,255,255,0.25)';
    } else {
        menu.style.opacity = '0';
        menu.style.visibility = 'hidden';
        menu.style.transform = 'translateY(-10px)';
        arrow.style.transform = 'rotate(0deg)';
        trigger.style.background = 'rgba(255,255,255,0.15)';
    }
}

function closeDropdown() {
    const menu = parent.document.getElementById('dropdown-menu');
    const arrow = parent.document.getElementById('dropdown-arrow');
    const trigger = parent.document.getElementById('dropdown-trigger');
    
    if (!menu || !arrow || !trigger) return;
    
    dropdownOpen = false;
    menu.style.opacity = '0';
    menu.style.visibility = 'hidden';
    menu.style.transform = 'translateY(-10px)';
    arrow.style.transform = 'rotate(0deg)';
    trigger.style.background = 'rgba(255,255,255,0.15)';
}

function triggerLogout() {
    // Direct logout action using Streamlit's page navigation
    if (parent.window.location) {
        parent.window.location.href = '/';
    }
    // Alternative: trigger a page reload to login
    parent.window.location.reload();
}

function triggerProfile() {
    // Show profile info or navigate to profile page
    alert('User Profile functionality - This can be customized to show profile details or navigate to a profile page.');
}

// Setup dropdown functionality
function setupDropdown() {
    const trigger = parent.document.getElementById('dropdown-trigger');
    const logoutItem = parent.document.getElementById('logout-item');
    const profileItem = parent.document.getElementById('user-profile-item');
    
    if (trigger && !trigger.hasAttribute('data-initialized')) {
        trigger.setAttribute('data-initialized', 'true');
        trigger.onclick = function(e) {
            e.stopPropagation();
            toggleDropdown();
        };
    }
    
    if (logoutItem && !logoutItem.hasAttribute('data-initialized')) {
        logoutItem.setAttribute('data-initialized', 'true');
        logoutItem.onclick = function() {
            closeDropdown();
            triggerLogout();
        };
        
        logoutItem.onmouseenter = function() {
            this.style.background = 'rgba(220, 38, 38, 0.1)';
        };
        
        logoutItem.onmouseleave = function() {
            this.style.background = 'transparent';
        };
    }
    
    if (profileItem && !profileItem.hasAttribute('data-initialized')) {
        profileItem.setAttribute('data-initialized', 'true');
        profileItem.onclick = function() {
            closeDropdown();
            triggerProfile();
        };
        
        profileItem.onmouseenter = function() {
            this.style.background = 'rgba(23, 32, 135, 0.1)';
        };
        
        profileItem.onmouseleave = function() {
            this.style.background = 'transparent';
        };
    }
    
    // Close dropdown when clicking outside
    parent.document.onclick = function(e) {
        const dropdown = parent.document.getElementById('dropdown-menu');
        const trigger = parent.document.getElementById('dropdown-trigger');
        
        if (dropdown && trigger && 
            !dropdown.contains(e.target) && 
            !trigger.contains(e.target)) {
            closeDropdown();
        }
    };
}

// Initialize with retries
setTimeout(setupDropdown, 100);
setTimeout(setupDropdown, 500);
setTimeout(setupDropdown, 1000);
</script>
""", height=0)

# Move ALL content directly under header - Aggressive spacing reduction
st.markdown("""
<style>
/* Aggressive spacing reduction - content starts immediately after header */
.main .block-container {
    padding-top: 55px !important;
    padding-bottom: 1rem !important;
    margin-top: 0 !important;
}
.stApp > div:first-child {
    padding-top: 0px !important;
    margin-top: 0 !important;
}
/* Remove ALL default Streamlit spacing */
div[data-testid="stVerticalBlock"] {
    margin-top: 0 !important;
    padding-top: 0 !important;
}
div[data-testid="stVerticalBlock"] > div:first-child {
    margin-top: 0 !important;
    padding-top: 0 !important;
}
/* Force admin info panel to start immediately with no gaps */
.admin-info-panel {
    margin-top: 0 !important;
    margin-bottom: 1rem !important;
    padding-top: 0 !important;
}
/* Reduce navigation spacing dramatically */
.navigation-container {
    margin-top: 0.5rem;
    margin-bottom: 1rem;
}
/* Move navigation buttons up aggressively */
div[data-testid="stHorizontalBlock"]:first-of-type {
    margin-top: 0rem !important;
    margin-bottom: 1rem !important;
}
div[data-testid="stHorizontalBlock"]:nth-of-type(2) {
    margin-top: 0.5rem !important;
    margin-bottom: 1rem !important;
}
/* Reduce content section spacing */
.content-section {
    margin-top: 0.5rem !important;
    padding-top: 0 !important;
}
/* Reduce content header spacing */
.content-header {
    margin-bottom: 1rem !important;
    padding-bottom: 0.5rem !important;
}
</style>
""", unsafe_allow_html=True)

# Admin Info Panel (moved up, no white space)
admin_info = get_admin_credentials_display()
auth_cookie = st.session_state["auth_cookie"]
current_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")

st.markdown(f"""
    <div class="admin-info-panel">
        <div class="admin-info-grid">
            <div class="admin-info-item">
                <span class="admin-info-label">Admin:</span>
                <span class="admin-info-value">{auth_cookie.get('first_name', 'DTI')} {auth_cookie.get('last_name', 'Administrator')}</span>
            </div>
            <div class="admin-info-item">
                <span class="admin-info-label">Session:</span>
                <span class="admin-info-value">{session_manager.get_browser_id()[:12]}...</span>
            </div>
            <div class="admin-info-item">
                <span class="admin-info-label">Last Access:</span>
                <span class="admin-info-value">{current_time}</span>
            </div>
            <div class="admin-info-item">
                <span class="admin-info-label">Username:</span>
                <span class="admin-info-value">{admin_info['username']}</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Navigation Menu - Table Format
st.markdown("""
<style>
.nav-table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;
    background: white;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.nav-table td {
    padding: 15px 20px;
    text-align: center;
    border: 1px solid #e0e0e0;
    cursor: pointer;
    transition: all 0.3s ease;
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    position: relative;
}

.nav-table td:hover {
    background: linear-gradient(135deg, #172087 0%, #1e3a8a 100%);
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(23, 32, 135, 0.3);
}

.nav-table td.active {
    background: linear-gradient(135deg, #172087 0%, #1e3a8a 100%);
    color: white;
    font-weight: bold;
}

.nav-title {
    font-weight: 600;
    font-size: 14px;
    margin-bottom: 2px;
    display: block;
}

.nav-desc {
    font-size: 11px;
    opacity: 0.8;
    display: block;
}

.nav-table td.active .nav-desc {
    opacity: 0.9;
}
</style>
""", unsafe_allow_html=True)

# Create navigation table
selected_tab = st.session_state.get("admin_selected_tab", "Dashboard Overview")

# Zero-spacing override CSS
st.markdown("""
<style>
/* Ultra-compact layout overrides */
.main .block-container {
    padding-top: 51px !important;
    padding-bottom: 0 !important;
    margin: 0 auto !important;
}

/* Zero spacing for all elements */
.stApp > div:first-child,
div[data-testid="stVerticalBlock"],
div[data-testid="stHorizontalBlock"],
.element-container,
.stMarkdown,
.row-widget,
div[class*="css-"] {
    margin: 0 !important;
    padding: 0 !important;
}

/* Minimal admin panel spacing */
.admin-info-panel {
    margin: 0 0 0.5rem 0 !important;
    padding: 0.75rem !important;
}

/* Compressed navigation spacing */
.navigation-section {
    margin: 0 0 0.5rem 0 !important;
}

/* Tight button spacing */
div[data-testid="stHorizontalBlock"]:first-of-type {
    margin: 0 0 0.25rem 0 !important;
}

/* Second row of navigation buttons with proper gap */
div[data-testid="stHorizontalBlock"]:nth-of-type(2) {
    margin-top: 1.5rem;
    margin-bottom: 2rem;
}

/* Button styling consistency */
.stButton > button {
    width: 100%;
    height: 3rem;
    border-radius: 8px;
    font-weight: 500;
}

/* ===== CONTENT AREA SPACING ===== */
/* Proper content spacing after navigation */
.content-section {
    margin-top: 2rem;
    padding-top: 1rem;
}

/* Content header spacing */
.content-header {
    margin-bottom: 1.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e5e7eb;
}
</style>
""", unsafe_allow_html=True)

# Display table navigation using columns for better Streamlit integration
col1, col2, col3, col4 = st.columns(4)

# First row navigation
with col1:
    section = admin_sections[0]
    is_active = selected_tab == section["title"]
    button_type = "primary" if is_active else "secondary"
    if st.button(f"{section['title']}", key=f"nav_btn_{section['id']}", 
                type=button_type, use_container_width=True, 
                help=section['description']):
        st.session_state["admin_selected_tab"] = section["title"]
        st.rerun()

with col2:
    section = admin_sections[1]
    is_active = selected_tab == section["title"]
    button_type = "primary" if is_active else "secondary"
    if st.button(f"{section['title']}", key=f"nav_btn_{section['id']}", 
                type=button_type, use_container_width=True, 
                help=section['description']):
        st.session_state["admin_selected_tab"] = section["title"]
        st.rerun()

with col3:
    section = admin_sections[2]
    is_active = selected_tab == section["title"]
    button_type = "primary" if is_active else "secondary"
    if st.button(f"{section['title']}", key=f"nav_btn_{section['id']}", 
                type=button_type, use_container_width=True, 
                help=section['description']):
        st.session_state["admin_selected_tab"] = section["title"]
        st.rerun()

with col4:
    section = admin_sections[3]
    is_active = selected_tab == section["title"]
    button_type = "primary" if is_active else "secondary"
    if st.button(f"{section['title']}", key=f"nav_btn_{section['id']}", 
                type=button_type, use_container_width=True, 
                help=section['description']):
        st.session_state["admin_selected_tab"] = section["title"]
        st.rerun()

# Second row navigation
col1, col2, col3, col4 = st.columns(4)

with col1:
    section = admin_sections[4]
    is_active = selected_tab == section["title"]
    button_type = "primary" if is_active else "secondary"
    if st.button(f"{section['title']}", key=f"nav_btn_{section['id']}", 
                type=button_type, use_container_width=True, 
                help=section['description']):
        st.session_state["admin_selected_tab"] = section["title"]
        st.rerun()

with col2:
    section = admin_sections[5]
    is_active = selected_tab == section["title"]
    button_type = "primary" if is_active else "secondary"
    if st.button(f"{section['title']}", key=f"nav_btn_{section['id']}", 
                type=button_type, use_container_width=True, 
                help=section['description']):
        st.session_state["admin_selected_tab"] = section["title"]
        st.rerun()

with col3:
    section = admin_sections[6]
    is_active = selected_tab == section["title"]
    button_type = "primary" if is_active else "secondary"
    if st.button(f"{section['title']}", key=f"nav_btn_{section['id']}", 
                type=button_type, use_container_width=True, 
                help=section['description']):
        st.session_state["admin_selected_tab"] = section["title"]
        st.rerun()

with col4:
    section = admin_sections[7]
    is_active = selected_tab == section["title"]
    button_type = "primary" if is_active else "secondary"
    if st.button(f"{section['title']}", key=f"nav_btn_{section['id']}", 
                type=button_type, use_container_width=True, 
                help=section['description']):
        st.session_state["admin_selected_tab"] = section["title"]
        st.rerun()

# Get current selected tab
selected_tab = st.session_state.get("admin_selected_tab", "Dashboard Overview")

# Content Area with proper spacing
st.markdown('<div class="content-section">', unsafe_allow_html=True)

# Content Header with active indicator
current_section = next((s for s in admin_sections if s["title"] == selected_tab), admin_sections[0])
st.markdown(f"""
    <div class="content-header">
        <h2 class="content-title">{selected_tab}</h2>
        <span class="content-badge">Active Page</span>
    </div>
""", unsafe_allow_html=True)

# Display content based on selected tab
if selected_tab == "Dashboard Overview":
    # System Metrics
    users = load_users()
    active_users = get_active_users()
    total_users = len(users)
    approved_users = len([u for u in users.values() if u.get("approved")])
    pending_users = total_users - approved_users
    online_count = len([u for u in active_users if u['status'] == 'online'])
    away_count = len([u for u in active_users if u['status'] == 'away'])
    idle_count = len([u for u in active_users if u['status'] == 'idle'])
    
    # Metrics Grid
    st.markdown("""
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">""" + str(total_users) + """</div>
                <div class="metric-label">Total Users</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">""" + str(approved_users) + """</div>
                <div class="metric-label">Approved Users</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">""" + str(pending_users) + """</div>
                <div class="metric-label">Pending Approvals</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">""" + str(online_count) + """</div>
                <div class="metric-label">Users Online</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Recent Activity Table
    st.markdown("### Recent User Activity")
    
    if active_users:
        # Create activity data for display
        activity_data = []
        for user in active_users[:10]:  # Show last 10 active users
            activity_data.append({
                "User": f"{user['full_name']} (@{user['username']})",
                "Status": user['status_text'],
                "Last Activity": format_time_ago(user['last_activity']),
                "Session Start": user.get('session_start', 'Unknown'),
                "Role": user['role'].title()
            })
        
        # Display as Streamlit dataframe with custom styling
        import pandas as pd
        df = pd.DataFrame(activity_data)
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "User": st.column_config.TextColumn("User", width="large"),
                "Status": st.column_config.TextColumn("Status", width="small"),
                "Last Activity": st.column_config.TextColumn("Last Activity", width="medium"),
                "Session Start": st.column_config.TextColumn("Session Start", width="medium"),
                "Role": st.column_config.TextColumn("Role", width="small")
            }
        )
    else:
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon"></div>
                <h3>No Active Users</h3>
                <p>No users are currently active in the system.</p>
            </div>
        """, unsafe_allow_html=True)

elif selected_tab == "Pending Approvals":
    users = load_users()
    pending_users = {username: user_data for username, user_data in users.items() 
                    if user_data.get("role") == "encoder" and not user_data.get("approved")}
    
    if not pending_users:
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon"></div>
                <h3>No Pending Approvals</h3>
                <p>All user registrations have been processed.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"### {len(pending_users)} Pending User Registrations")
        
        # Create table with clickable headers
        table_html = """
        <table class="data-table">
            <thead>
                <tr>
                    <th>👤 User Details</th>
                    <th>📧 Contact Information</th>
                    <th>🏢 Organization</th>
                    <th>📅 Registration</th>
                    <th>⚡ Actions</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for username, user_data in pending_users.items():
            table_html += f"""
                <tr>
                    <td>
                        <strong>{user_data.get('first_name', '')} {user_data.get('last_name', '')}</strong><br>
                        <small>@{username}</small>
                    </td>
                    <td>
                        📧 {user_data.get('email', 'N/A')}<br>
                        📞 {user_data.get('contact_number', 'N/A')}
                    </td>
                    <td>
                        <strong>{user_data.get('organization', 'N/A')}</strong><br>
                        <small>{user_data.get('position', 'N/A')}</small>
                    </td>
                    <td>
                        {format_timestamp(user_data.get('created_at', 0))}<br>
                        <small>Status: Pending</small>
                    </td>
                    <td>
                        <div style="display: flex; gap: 0.5rem; flex-direction: column;">
                            See actions below table
                        </div>
                    </td>
                </tr>
            """
        
        table_html += "</tbody></table>"
        st.markdown(table_html, unsafe_allow_html=True)
        
        # Action buttons below table
        st.markdown("#### Quick Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            selected_user = st.selectbox("Select user to approve:", list(pending_users.keys()))
            if st.button("✓ Approve Selected User", type="primary", use_container_width=True):
                users[selected_user]["approved"] = True
                users[selected_user]["approved_at"] = time.time()
                users[selected_user]["approved_by"] = auth_cookie.get("username", "admin")
                save_users(users)
                
                email_sent = send_approval_notification(pending_users[selected_user])
                st.success(f"User {selected_user} approved successfully!")
                if email_sent:
                    st.success("Approval email sent to user.")
                else:
                    st.warning("User approved, but email notification failed.")
                st.rerun()
        
        with col2:
            selected_reject_user = st.selectbox("Select user to reject:", list(pending_users.keys()), key="reject_select")
            if st.button("✗ Reject Selected User", type="secondary", use_container_width=True):
                email_sent = send_rejection_notification(pending_users[selected_reject_user])
                del users[selected_reject_user]
                save_users(users)
                
                st.success(f"User {selected_reject_user} rejected and removed.")
                if email_sent:
                    st.success("Rejection email sent to user.")
                else:
                    st.warning("User rejected, but email notification failed.")
                st.rerun()

elif selected_tab == "Active Users":
    active_users = get_active_users()
    
    # Auto-refresh controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"### {len(active_users)} Currently Active Users")
    with col2:
        auto_refresh = st.checkbox("Auto-refresh (30s)", value=False, key="auto_refresh_users")
    with col3:
        if st.button("Refresh Now", key="manual_refresh_users"):
            st.rerun()
    
    if auto_refresh:
        time.sleep(30)
        st.rerun()
    
    if not active_users:
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon"></div>
                <h3>No Active Users</h3>
                <p>No users are currently active in the system.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### Status Definitions:")
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
        
        def create_users_display(users_list, status_type):
            if not users_list:
                st.markdown(f"""
                    <div class="empty-state">
                        <div class="empty-state-icon"></div>
                        <h4>No {status_type} Users</h4>
                        <p>No users are currently {status_type.lower()}.</p>
                    </div>
                """, unsafe_allow_html=True)
                return
            
            # Create data for Streamlit display
            user_data = []
            for user in users_list:
                session_start = user.get('session_start', 'unknown')
                if session_start != 'unknown':
                    try:
                        start_time = datetime.fromisoformat(session_start)
                        session_display = start_time.strftime('%H:%M')
                    except:
                        session_display = "Unknown"
                else:
                    session_display = "Unknown"
                
                user_data.append({
                    "User": f"{user['full_name']} (@{user['username']})",
                    "Status": f"● {user['status_text']}",
                    "Last Activity": format_time_ago(user['last_activity']),
                    "Session Started": session_display,
                    "Role": user['role'].title()
                })
            
            # Display as Streamlit dataframe
            import pandas as pd
            df = pd.DataFrame(user_data)
            
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "User": st.column_config.TextColumn("User", width="large"),
                    "Status": st.column_config.TextColumn("Status", width="small"),
                    "Last Activity": st.column_config.TextColumn("Last Activity", width="medium"),
                    "Session Started": st.column_config.TextColumn("Session Started", width="medium"),
                    "Role": st.column_config.TextColumn("Role", width="small")
                }
            )
        
        with tab1:
            create_users_display(online_users, "Online")
        
        with tab2:
            create_users_display(away_users, "Away")
        
        with tab3:
            create_users_display(idle_users, "Idle")

elif selected_tab == "All Users":
    users = load_users()
    
    st.markdown(f"### {len(users)} Registered Users")
    
    if users:
        # Create user data for Streamlit display
        user_data_list = []
        non_admin_users = []
        
        for username, user_data in users.items():
            status = "Approved" if user_data.get("approved") else "Pending"
            role = user_data.get("role", "encoder").title()
            
            user_display = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}" 
            if not user_display.strip():
                user_display = username
            
            created_date = format_timestamp(user_data.get('created_at', 0))
            approved_info = ""
            if user_data.get("approved_at"):
                approved_date = format_timestamp(user_data.get('approved_at', 0))
                approved_by = user_data.get('approved_by', 'Unknown')
                approved_info = f"{approved_date} by {approved_by}"
            
            user_data_list.append({
                "User": f"{user_display} (@{username})",
                "Role": role,
                "Email": user_data.get('email', 'N/A'),
                "Contact": user_data.get('contact_number', 'N/A'),
                "Organization": user_data.get('organization', 'N/A'),
                "Position": user_data.get('position', 'N/A'),
                "Status": status,
                "Created": created_date,
                "Approved": approved_info if approved_info else "Not approved"
            })
            
            if user_data.get("role") != "admin":
                non_admin_users.append(username)
        
        # Display as Streamlit dataframe
        import pandas as pd
        df = pd.DataFrame(user_data_list)
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "User": st.column_config.TextColumn("User", width="large"),
                "Role": st.column_config.TextColumn("Role", width="small"),
                "Email": st.column_config.TextColumn("Email", width="medium"),
                "Contact": st.column_config.TextColumn("Contact", width="medium"),
                "Organization": st.column_config.TextColumn("Organization", width="medium"),
                "Position": st.column_config.TextColumn("Position", width="medium"),
                "Status": st.column_config.TextColumn("Status", width="small"),
                "Created": st.column_config.TextColumn("Created", width="medium"),
                "Approved": st.column_config.TextColumn("Approved", width="medium")
            }
        )
        
        # Action area below table with visual separation
        st.markdown("---")  # Add separator line
        st.markdown("#### User Management Actions")
        
        # Create management actions table
        non_admin_users = [username for username, user_data in users.items() if user_data.get("role") != "admin"]
        
        if non_admin_users:
            # User deletion interface in table format
            import pandas as pd
            
            # Statistics data
            total_users = len(users)
            approved_count = len([u for u in users.values() if u.get("approved")])
            pending_count = total_users - approved_count
            admin_count = len([u for u in users.values() if u.get("role") == "admin"])
            
            # Create management data for table display
            management_data = [
                {"Action Type": "User Deletion", "Available Users": len(non_admin_users), "Status": "Ready"},
                {"Action Type": "Total Users", "Available Users": total_users, "Status": "Active"},
                {"Action Type": "Approved Users", "Available Users": approved_count, "Status": "Verified"},
                {"Action Type": "Pending Users", "Available Users": pending_count, "Status": "Waiting"},
                {"Action Type": "Admin Users", "Available Users": admin_count, "Status": "Protected"}
            ]
            
            df_management = pd.DataFrame(management_data)
            st.dataframe(
                df_management,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Action Type": st.column_config.TextColumn("Action Type", width="medium"),
                    "Available Users": st.column_config.NumberColumn("Count", width="small"),
                    "Status": st.column_config.TextColumn("Status", width="small")
                }
            )
            
            # User deletion controls below table
            st.markdown("**User Deletion Controls:**")
            
            # Create user deletion table with buttons
            deletion_table_data = []
            for username in non_admin_users:
                user_data = users[username]
                user_display = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
                display_name = user_display if user_display else username
                
                deletion_table_data.append({
                    "Username": username,
                    "Full Name": display_name,
                    "Email": user_data.get('email', 'N/A'),
                    "Role": user_data.get('role', 'user'),
                    "Status": "Active"
                })
            
            if deletion_table_data:
                df_deletion = pd.DataFrame(deletion_table_data)
                st.dataframe(
                    df_deletion,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Username": st.column_config.TextColumn("Username", width="medium"),
                        "Full Name": st.column_config.TextColumn("Full Name", width="medium"),
                        "Email": st.column_config.TextColumn("Email", width="medium"),
                        "Role": st.column_config.TextColumn("Role", width="small"),
                        "Status": st.column_config.TextColumn("Status", width="small")
                    }
                )
                
                # Deletion action buttons
                st.markdown("**Select User to Delete:**")
                
                # Create buttons in rows of maximum 3 columns
                for i in range(0, len(non_admin_users), 3):
                    cols = st.columns(3)
                    for j, col in enumerate(cols):
                        if i + j < len(non_admin_users):
                            username = non_admin_users[i + j]
                            with col:
                                if st.button(f"🗑️ Delete {username}", key=f"delete_{username}", type="secondary", use_container_width=True):
                                    # Confirm deletion with a confirmation step
                                    if f"confirm_delete_{username}" not in st.session_state:
                                        st.session_state[f"confirm_delete_{username}"] = True
                                        st.warning(f"Click again to confirm deletion of {username}")
                                        st.rerun()
                                    else:
                                        # Backup deleted user
                                        backup_deleted_user(username, users[username])
                                        # Remove user from active users
                                        del users[username]
                                        save_users(users)
                                        # Clear confirmation state
                                        del st.session_state[f"confirm_delete_{username}"]
                                        st.success(f"User {username} deleted successfully!")
                                        st.rerun()
        else:
            # Empty state table
            import pandas as pd
            empty_data = [{"Message": "No non-admin users available for deletion", "Status": "No Action Required"}]
            df_empty = pd.DataFrame(empty_data)
            st.dataframe(df_empty, use_container_width=True, hide_index=True)
    else:
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon"></div>
                <h3>No Users Found</h3>
                <p>No users are registered in the system.</p>
            </div>
        """, unsafe_allow_html=True)

elif selected_tab == "User Data Management":
    # Get all users
    all_users = load_users()
    regular_users = {k: v for k, v in all_users.items() if v.get("role") != "admin"}
    
    if regular_users:
        st.markdown(f"### Data Management for {len(regular_users)} Users")
        
        # Check for user data files
        from utils.data_manager import data_manager
        
        # Create user data list for table display
        user_data_list = []
        
        for username, user_data in regular_users.items():
            user_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
            display_name = user_name if user_name else username
            
            # Check if user has data
            has_data = data_manager.user_has_data(username)
            status_text = "Has Data" if has_data else "No Data"
            
            # Get data summary
            if has_data:
                summary = get_user_data_summary(username)
                total_records = sum(summary.values()) if summary else 0
            else:
                total_records = 0
            
            approval_status = "Approved" if user_data.get('approved') else "Pending"
            
            user_data_list.append({
                "User": f"{display_name} (@{username})",
                "Status": approval_status,
                "Email": user_data.get('email', 'N/A'),
                "Organization": user_data.get('organization', 'N/A'),
                "Data Status": status_text,
                "Total Records": total_records,
                "Actions": "See options below table"
            })
        
        # Display as Streamlit dataframe
        import pandas as pd
        df = pd.DataFrame(user_data_list)
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "User": st.column_config.TextColumn("User", width="large"),
                "Status": st.column_config.TextColumn("Status", width="small"),
                "Email": st.column_config.TextColumn("Email", width="medium"),
                "Organization": st.column_config.TextColumn("Organization", width="medium"),
                "Data Status": st.column_config.TextColumn("Data Status", width="small"),
                "Total Records": st.column_config.NumberColumn("Total Records", width="small"),
                "Actions": st.column_config.TextColumn("Actions", width="medium")
            }
        )
        
        # Action area below table
        st.markdown("#### Data Management Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**User Selection:**")
            users_with_data = [username for username, user_data in regular_users.items() 
                             if data_manager.user_has_data(username)]
            
            if users_with_data:
                selected_user = st.selectbox("Select user for data operations:", users_with_data)
                
                if st.button("Check Duplicates", key="check_dupes_selected", use_container_width=True):
                    st.session_state["show_duplicates_selected"] = selected_user
                    st.rerun()
                
                if st.button("View Summary", key="view_summary_selected", use_container_width=True):
                    st.session_state["show_summary_selected"] = selected_user
                    st.rerun()
            else:
                st.info("No users with data available")
        
        with col2:
            st.markdown("**Data Statistics:**")
            total_users_with_data = len([u for u in regular_users.keys() if data_manager.user_has_data(u)])
            total_users_without_data = len(regular_users) - total_users_with_data
            total_all_records = sum([sum(get_user_data_summary(u).values()) for u in regular_users.keys() if data_manager.user_has_data(u)])
            
            st.write(f"Users with Data: **{total_users_with_data}**")
            st.write(f"Users without Data: **{total_users_without_data}**")
            st.write(f"Total Records: **{total_all_records}**")
        
        # Show detailed results if requested
        if "show_duplicates_selected" in st.session_state:
            username = st.session_state["show_duplicates_selected"]
            st.markdown(f"#### Duplicate Check Results for @{username}")
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
            
            if st.button("Close Duplicate Results", key="close_dupes_selected"):
                del st.session_state["show_duplicates_selected"]
                st.rerun()
        
        # Show data summary if requested
        if "show_summary_selected" in st.session_state:
            username = st.session_state["show_summary_selected"]
            st.markdown(f"#### Data Summary for @{username}")
            summary = get_user_data_summary(username)
            
            if summary:
                summary_data = []
                for sheet_name, count in summary.items():
                    if count > 0:
                        summary_data.append({
                            "Sheet Name": sheet_name,
                            "Record Count": count
                        })
                
                if summary_data:
                    summary_df = pd.DataFrame(summary_data)
                    st.dataframe(
                        summary_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Sheet Name": st.column_config.TextColumn("Sheet Name", width="large"),
                            "Record Count": st.column_config.NumberColumn("Record Count", width="small")
                        }
                    )
                else:
                    st.info("No data records found")
            else:
                st.info("No data found")
            
            if st.button("Close Summary Results", key="close_summary_selected"):
                del st.session_state["show_summary_selected"]
                st.rerun()
    else:
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon"></div>
                <h3>No Regular Users</h3>
                <p>No regular users are registered yet.</p>
            </div>
        """, unsafe_allow_html=True)

elif selected_tab == "System Data Analysis":
    st.markdown("### System-Wide Data Analysis")
    st.markdown("*Comprehensive data scanning across all users - like analyzing an entire Excel workbook*")
    
    # System-wide duplicate detection
    st.markdown("#### System-Wide Duplicate Detection")
    st.info("This tool scans ALL user data to find identical entries across different encoders.")
    
    if st.button("Scan All User Data for Duplicates", type="primary", use_container_width=True):
        with st.spinner("Scanning all user data... This may take a moment."):
            system_duplicates = check_system_wide_duplicates()
        
        if system_duplicates:
            st.markdown("#### System-Wide Duplicates Found")
            
            for sheet_name, sheet_duplicates in system_duplicates.items():
                st.markdown(f"##### {sheet_name} Sheet")
                
                duplicates_html = """
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Field</th>
                            <th>Duplicate Value</th>
                            <th>Occurrences</th>
                            <th>Encoders Involved</th>
                            <th>Severity</th>
                        </tr>
                    </thead>
                    <tbody>
                """
                
                for field, duplicates in sheet_duplicates.items():
                    for dup_info in duplicates:
                        value = dup_info['value']
                        total = dup_info['total_occurrences']
                        encoder_count = dup_info['encoders_involved']
                        is_cross_encoder = dup_info['cross_encoder']
                        
                        severity = "CRITICAL" if is_cross_encoder else "WARNING"
                        severity_class = "status-pending" if is_cross_encoder else "status-approved"
                        
                        encoder_details = []
                        for encoder_detail in dup_info['encoder_details']:
                            encoder = encoder_detail['encoder']
                            count = encoder_detail['count']
                            encoder_details.append(f"{encoder} ({count})")
                        
                        duplicates_html += f"""
                            <tr>
                                <td><strong>{field}</strong></td>
                                <td>{value}</td>
                                <td>{total}</td>
                                <td>{', '.join(encoder_details)}</td>
                                <td><span class="{severity_class}">{severity}</span></td>
                            </tr>
                        """
                
                duplicates_html += """
                    </tbody>
                </table>
                """
                
                st.markdown(duplicates_html, unsafe_allow_html=True)
        else:
            st.success("**No system-wide duplicates found!** All data appears to be unique across all users.")
    
    st.markdown("---")
    
    # Data distribution analysis
    st.markdown("#### Data Distribution Analysis")
    
    if st.button("Analyze Data Distribution", type="secondary", use_container_width=True):
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
        st.markdown("""
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">""" + str(total_records) + """</div>
                    <div class="metric-label">Total System Records</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">""" + str(len([u for u in user_data_summary.values() if u['total_records'] > 0])) + """</div>
                    <div class="metric-label">Active Data Users</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">""" + str(len([u for u in user_data_summary.values() if u['total_records'] == 0])) + """</div>
                    <div class="metric-label">Empty Users</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">""" + f"{total_records / len(regular_users) if regular_users else 0:.1f}" + """</div>
                    <div class="metric-label">Avg Records/User</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Show per-user breakdown
        st.markdown("#### Per-User Data Breakdown")
        
        # Sort users by total records (descending)
        sorted_users = sorted(user_data_summary.items(), key=lambda x: x[1]['total_records'], reverse=True)
        
        breakdown_html = """
        <table class="data-table">
            <thead>
                <tr>
                    <th>User</th>
                    <th>Total Records</th>
                    <th>Top Sheets</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for username, data_info in sorted_users:
            user_data = regular_users[username]
            user_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
            display_name = user_name if user_name else username
            
            total = data_info['total_records']
            sheet_data = data_info['sheet_breakdown']
            active_sheets = {k: v for k, v in sheet_data.items() if v > 0}
            
            # Get top 3 sheets
            top_sheets = sorted(active_sheets.items(), key=lambda x: x[1], reverse=True)[:3]
            sheet_summary = ', '.join([f"{sheet}: {count}" for sheet, count in top_sheets])
            
            status = "Active" if total > 0 else "Empty"
            status_class = "status-approved" if total > 0 else "status-pending"
            
            breakdown_html += f"""
                <tr>
                    <td>
                        <strong>{display_name}</strong><br>
                        <small>@{username}</small>
                    </td>
                    <td><strong>{total}</strong></td>
                    <td>{sheet_summary if sheet_summary else 'No data'}</td>
                    <td><span class="{status_class}">{status}</span></td>
                </tr>
            """
        
        breakdown_html += """
            </tbody>
        </table>
        """
        
        st.markdown(breakdown_html, unsafe_allow_html=True)

elif selected_tab == "System Settings":
    users = load_users()
    total_users = len(users)
    approved_users = len([u for u in users.values() if u.get("approved")])
    pending_users = total_users - approved_users
    
    st.markdown("### System Configuration")
    
    # System metrics
    st.markdown("""
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">""" + str(total_users) + """</div>
                <div class="metric-label">Total Users</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">""" + str(approved_users) + """</div>
                <div class="metric-label">Approved Users</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">""" + str(pending_users) + """</div>
                <div class="metric-label">Pending Approvals</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">""" + str(session_manager.get_active_sessions_count()) + """</div>
                <div class="metric-label">Active Sessions</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Admin Configuration
    st.markdown("#### Admin Configuration")
    admin_info = get_admin_credentials_display()
    
    admin_config_html = f"""
    <table class="data-table">
        <thead>
            <tr>
                <th>Setting</th>
                <th>Value</th>
                <th>Description</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Username</strong></td>
                <td><code>{admin_info['username']}</code></td>
                <td>Administrator login username</td>
            </tr>
            <tr>
                <td><strong>Email</strong></td>
                <td><code>{admin_info['email']}</code></td>
                <td>Administrator email address</td>
            </tr>
            <tr>
                <td><strong>Name</strong></td>
                <td>{admin_info['name']}</td>
                <td>Administrator full name</td>
            </tr>
            <tr>
                <td><strong>Password</strong></td>
                <td><code>{admin_info['password']}</code></td>
                <td>Secure password (hidden)</td>
            </tr>
        </tbody>
    </table>
    """
    
    st.markdown(admin_config_html, unsafe_allow_html=True)
    
    st.info("Admin credentials are stored securely in Streamlit secrets")
    
    if st.button("Reset Admin Account", help="This will recreate the admin account with current settings"):
        try:
            # Remove existing admin and recreate
            users = load_users()
            admin_keys_to_remove = [k for k, v in users.items() if v.get("role") == "admin"]
            for key in admin_keys_to_remove:
                del users[key]
            
            created, message = create_admin_if_not_exists(users)
            if created:
                save_users(users)
                st.success("Admin account reset successfully!")
                st.rerun()
            else:
                st.warning("Could not reset admin account")
        except Exception as e:
            st.error(f"Error resetting admin account: {str(e)}")

elif selected_tab == "Deleted Users":
    backup_data = load_deleted_users_backup()
    
    if not backup_data:
        st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon"></div>
                <h3>No Deleted Users</h3>
                <p>No users have been deleted from the system.</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"### {len(backup_data)} Deleted Users")
        
        # Create deleted user data for Streamlit display
        deleted_user_list = []
        
        for username, user_data in backup_data.items():
            deleted_at = user_data.get("deleted_at", 0)
            deleted_by = user_data.get("deleted_by", "Unknown")
            created_at = format_timestamp(user_data.get('created_at', 0))
            
            user_display = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
            display_name = user_display if user_display else username
            
            deleted_user_list.append({
                "User": f"{display_name} (@{username})",
                "Email": user_data.get('email', 'N/A'),
                "Contact": user_data.get('contact_number', 'N/A'),
                "Organization": user_data.get('organization', 'N/A'),
                "Position": user_data.get('position', 'N/A'),
                "Created": created_at,
                "Deleted": format_timestamp(deleted_at),
                "Deleted By": deleted_by,
                "Status": "Deleted User"
            })
        
        # Display as Streamlit dataframe
        import pandas as pd
        df = pd.DataFrame(deleted_user_list)
        
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "User": st.column_config.TextColumn("User", width="large"),
                "Email": st.column_config.TextColumn("Email", width="medium"),
                "Contact": st.column_config.TextColumn("Contact", width="medium"),
                "Organization": st.column_config.TextColumn("Organization", width="medium"),
                "Position": st.column_config.TextColumn("Position", width="medium"),
                "Created": st.column_config.TextColumn("Created", width="medium"),
                "Deleted": st.column_config.TextColumn("Deleted", width="medium"),
                "Deleted By": st.column_config.TextColumn("Deleted By", width="small"),
                "Status": st.column_config.TextColumn("Status", width="small")
            }
        )
        
        # Restoration area below table with visual separation
        st.markdown("---")  # Add separator line
        st.markdown("#### User Restoration")
        
        # Create restoration summary table
        import pandas as pd
        
        # Create restoration data for table display
        restoration_data = [
            {"Restoration Type": "Available Backups", "Count": len(backup_data), "Status": "Ready"},
            {"Restoration Type": "Total Deleted Users", "Count": len(backup_data), "Status": "Archived"},
            {"Restoration Type": "Restoration Actions", "Count": 1, "Status": "Available"}
        ]
        
        df_restoration = pd.DataFrame(restoration_data)
        st.dataframe(
            df_restoration,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Restoration Type": st.column_config.TextColumn("Restoration Type", width="medium"),
                "Count": st.column_config.NumberColumn("Count", width="small"),
                "Status": st.column_config.TextColumn("Status", width="small")
            }
        )
        
        # User restoration controls below table
        st.markdown("**User Restoration Controls:**")
        
        # Create user restoration table with buttons
        restoration_table_data = []
        for username, user_data in backup_data.items():
            user_display = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
            display_name = user_display if user_display else username
            deleted_at = format_timestamp(user_data.get("deleted_at", 0))
            deleted_by = user_data.get("deleted_by", "Unknown")
            
            restoration_table_data.append({
                "Username": username,
                "Full Name": display_name,
                "Email": user_data.get('email', 'N/A'),
                "Deleted Date": deleted_at,
                "Deleted By": deleted_by
            })
        
        if restoration_table_data:
            df_restore = pd.DataFrame(restoration_table_data)
            st.dataframe(
                df_restore,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Username": st.column_config.TextColumn("Username", width="medium"),
                    "Full Name": st.column_config.TextColumn("Full Name", width="medium"),
                    "Email": st.column_config.TextColumn("Email", width="medium"),
                    "Deleted Date": st.column_config.TextColumn("Deleted Date", width="medium"),
                    "Deleted By": st.column_config.TextColumn("Deleted By", width="small")
                }
            )
            
            # Restoration action buttons
            st.markdown("**Select User to Restore:**")
            usernames = list(backup_data.keys())
            
            # Create buttons in rows of maximum 3 columns
            for i in range(0, len(usernames), 3):
                cols = st.columns(3)
                for j, col in enumerate(cols):
                    if i + j < len(usernames):
                        username = usernames[i + j]
                        with col:
                            if st.button(f"🔄 Restore {username}", key=f"restore_{username}", type="primary", use_container_width=True):
                                if restore_user_from_backup(username, backup_data):
                                    st.success(f"User {username} restored successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"Failed to restore user {username}")

# Content area closed
st.markdown('</div>', unsafe_allow_html=True)  # Close content-section div

# Footer with proper spacing
st.markdown("""
<div style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #e5e7eb;">
    <div style="text-align: center; margin-bottom: 1.5rem;">
        <strong>MSME CPMS Admin Dashboard</strong>
    </div>
</div>
""", unsafe_allow_html=True)

# Action buttons
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    pass  # Empty column for spacing

with col2:
    if st.button("Refresh Dashboard", use_container_width=True):
        st.rerun()

with col3:
    if st.button("🚪 Logout", use_container_width=True, type="primary"):
        st.session_state["authenticated"] = False
        st.session_state["auth_cookie"] = None
        session_manager.clear_session()
        st.switch_page("main.py")