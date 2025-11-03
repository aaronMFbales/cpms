import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from utils.philippine_locations import create_location_widgets
from utils.psic_handler import create_psic_widgets
from utils.data_manager import data_manager
from utils.secure_session import session_manager

# Try to import Excel libraries
try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

try:
    import xlsxwriter
    XLSXWRITER_AVAILABLE = True
except ImportError:
    XLSXWRITER_AVAILABLE = False

def save_targets_to_file(targets):
    """Save targets to a persistent file"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    targets_file = os.path.join(data_dir, "dashboard_targets.json")
    try:
        with open(targets_file, 'w') as f:
            json.dump(targets, f, indent=2)
    except Exception as e:
        st.error(f"Error saving targets: {e}")

def load_targets_from_file():
    """Load targets from persistent file"""
    targets_file = os.path.join("data", "dashboard_targets.json")
    default_targets = {
        'client_target': 50,
        'business_contact_target': 50,
        'business_registration_target': 40,
        'business_owner_target': 45,
        'employment_target': 30,
        'business_profiles_target': 35,
        'assistance_target': 25,
        'jobs_generated_target': 20
    }
    
    try:
        if os.path.exists(targets_file):
            with open(targets_file, 'r') as f:
                saved_targets = json.load(f)
                default_targets.update(saved_targets)
        return default_targets
    except Exception as e:
        st.error(f"Error loading targets: {e}")
        return default_targets

def load_all_data_from_file():
    """Load all user-specific data from all sheets"""
    try:
        auth_cookie = st.session_state.get("auth_cookie", {})
        username = auth_cookie.get("username", "anonymous")
        
        all_data = {}
        sheet_names = [
            "Business Owner", "Business Profile", "Client", "Business Registration",
            "Business Financial Structure", "Market Import", "Product Service Lines",
            "Employment Statistics", "Assistance", "Market Export", "Jobs Generated"
        ]
        
        for sheet_name in sheet_names:
            data, columns = data_manager.load_user_data(username, sheet_name)
            if data and columns:
                df = pd.DataFrame(data, columns=columns)
                all_data[sheet_name] = df.to_dict('records')
        
        return all_data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return {}

def create_user_excel_download():
    """Create Excel file for current user's data"""
    try:
        auth_cookie = st.session_state.get("auth_cookie", {})
        username = auth_cookie.get("username", "anonymous")
        user_full_name = f"{auth_cookie.get('first_name', '')} {auth_cookie.get('last_name', '')}".strip()
        
        output = io.BytesIO()
        sheet_names = [
            "Business Owner", "Business Profile", "Client", "Business Registration",
            "Business Financial Structure", "Market Import", "Product Service Lines", 
            "Employment Statistics", "Assistance", "Market Export", "Jobs Generated"
        ]
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            has_data = False
            
            for sheet_name in sheet_names:
                data, columns = data_manager.load_user_data(username, sheet_name)
                if data and columns:
                    df = pd.DataFrame(data, columns=columns)
                    if 'Date Created' in df.columns:
                        df['Date Created'] = df['Date Created'].astype(str)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    has_data = True
            
            if not has_data:
                summary_df = pd.DataFrame({
                    'Info': ['User', 'Export Date', 'Status'],
                    'Details': [user_full_name or username, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'No data records found']
                })
                summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        output.seek(0)
        return output.getvalue(), has_data, 'excel'
    except Exception as e:
        st.error(f"Error creating Excel file: {str(e)}")
        return None, False, None

def show():
    # Get authentication info
    auth_cookie = st.session_state.get("auth_cookie", {})
    username = auth_cookie.get("username", "anonymous")
    user_full_name = f"{auth_cookie.get('first_name', '')} {auth_cookie.get('last_name', '')}".strip()
    
    # Sidebar navigation
    with st.sidebar:
        st.title("CPMS Dashboard")
        st.caption("Client Profile and Monitoring System")
        
        # Navigation menu
        menu_items = [
            "Dashboard",
            "Client",
            "Business Contact Information", 
            "Business Registrations",
            "Business Owner",
            "Business Profile",
            "Business Financial Structure",
            "Market Domestic",
            "Market Export",
            "Market Import",
            "Product Service Lines",
            "Employment Statistics",
            "Assistance",
            "Jobs Generated"
        ]
        
        if "selected_nav_item" not in st.session_state:
            st.session_state.selected_nav_item = "Dashboard"
        
        for item in menu_items:
            if st.button(item, key=f"nav_{item}", use_container_width=True):
                st.session_state.selected_nav_item = item
                st.rerun()
        
        st.divider()
        st.subheader("User Profile")
        st.write(f"**Name:** {user_full_name}")
        st.write(f"**Role:** {auth_cookie.get('role', 'user').title()}")
        
        # Export Data
        st.divider()
        st.subheader("Export Data")
        result = create_user_excel_download()
        if result[0]:
            file_data, has_data, _ = result
            current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                "Download CPMS Data",
                data=file_data,
                file_name=f"CPMS_Data_{username}_{current_date}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        # Logout button
        st.divider()
        if st.button("Logout", type="primary", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["auth_cookie"] = None
            session_manager.clear_session()
            st.rerun()
    
    # Main content
    selected = st.session_state.selected_nav_item
    
    if selected == "Dashboard":
        # Load data and targets
        all_data = load_all_data_from_file()
        saved_targets = load_targets_from_file()
        
        st.title("CPMS Analytics Dashboard")
        st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        
        # Target setting
        with st.expander("Set Department Targets"):
            st.subheader("Department Targets")
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_client_target = st.number_input("Client Target", 
                    value=saved_targets['client_target'], min_value=1, max_value=1000)
                new_business_contact_target = st.number_input("Business Contact Target",
                    value=saved_targets['business_contact_target'], min_value=1, max_value=1000)
                new_business_registration_target = st.number_input("Business Registration Target",
                    value=saved_targets['business_registration_target'], min_value=1, max_value=1000)
                new_business_owner_target = st.number_input("Business Owner Target",
                    value=saved_targets['business_owner_target'], min_value=1, max_value=1000)
            
            with col2:
                new_business_profiles_target = st.number_input("Business Profiles Target",
                    value=saved_targets['business_profiles_target'], min_value=1, max_value=1000)
                new_employment_target = st.number_input("Employment Target",
                    value=saved_targets['employment_target'], min_value=1, max_value=1000)
                new_assistance_target = st.number_input("Assistance Target",
                    value=saved_targets['assistance_target'], min_value=1, max_value=1000)
                new_jobs_generated_target = st.number_input("Jobs Generated Target",
                    value=saved_targets['jobs_generated_target'], min_value=1, max_value=1000)
            
            if st.button("Update Targets", type="primary"):
                targets_to_save = {
                    'client_target': new_client_target,
                    'business_contact_target': new_business_contact_target,
                    'business_registration_target': new_business_registration_target,
                    'business_owner_target': new_business_owner_target,
                    'business_profiles_target': new_business_profiles_target,
                    'employment_target': new_employment_target,
                    'assistance_target': new_assistance_target,
                    'jobs_generated_target': new_jobs_generated_target
                }
                save_targets_to_file(targets_to_save)
                st.success("Targets updated successfully!")
                st.rerun()
        
        # Calculate metrics
        metrics = {
            'Clients': len(all_data.get('Client', [])),
            'Business Profiles': len(all_data.get('Business Profile', [])),
            'Business Registrations': len(all_data.get('Business Registrations', [])),
            'Employment Records': len(all_data.get('Employment Statistics', [])),
            'Assistance Provided': len(all_data.get('Assistance', [])),
            'Jobs Generated': len(all_data.get('Jobs Generated', []))
        }
        
        # Display metrics in columns
        st.subheader("Key Performance Indicators")
        col1, col2, col3 = st.columns(3)
        
        def display_metric(title, value, target):
            progress = min(value / target * 100, 100) if target > 0 else 0
            st.metric(
                label=title,
                value=value,
                delta=f"{progress:.1f}% of target"
            )
        
        with col1:
            display_metric("Registered Clients", 
                metrics['Clients'], saved_targets['client_target'])
            display_metric("Business Registrations",
                metrics['Business Registrations'], saved_targets['business_registration_target'])
        
        with col2:
            display_metric("Business Profiles",
                metrics['Business Profiles'], saved_targets['business_profiles_target'])
            display_metric("Employment Records",
                metrics['Employment Records'], saved_targets['employment_target'])
        
        with col3:
            display_metric("Assistance Provided",
                metrics['Assistance Provided'], saved_targets['assistance_target'])
            display_metric("Jobs Generated",
                metrics['Jobs Generated'], saved_targets['jobs_generated_target'])
        
        # Progress bars
        st.subheader("Progress Overview")
        for title, value in metrics.items():
            target = saved_targets.get(f"{title.lower().replace(' ', '_')}_target", 0)
            progress = value / target if target > 0 else 0
            st.progress(min(progress, 1.0), text=f"{title}: {value} of {target} ({progress*100:.1f}%)")
        
        # Recent activity
        st.subheader("Recent Activity")
        activity_data = []
        for sheet_name, records in all_data.items():
            for record in records[-5:]:  # Get last 5 records from each sheet
                if isinstance(record, dict) and 'Date Created' in record:
                    activity_data.append({
                        'Date': record['Date Created'],
                        'Type': sheet_name,
                        'Details': f"New {sheet_name} record added"
                    })
        
        if activity_data:
            df_activity = pd.DataFrame(activity_data)
            df_activity['Date'] = pd.to_datetime(df_activity['Date'])
            df_activity = df_activity.sort_values('Date', ascending=False).head(10)
            st.dataframe(df_activity, use_container_width=True)
        else:
            st.info("No recent activity found")