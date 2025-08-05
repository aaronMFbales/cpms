import streamlit as st
import numpy as np
import pandas as pd
import json
import os
from utils.philippine_locations import create_location_widgets

def save_data_to_file(sheet_name, data, columns):
    """Save data to Excel file with multiple sheets"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    excel_file = os.path.join(data_dir, "cpms_data.xlsx")
    
    # Convert data to DataFrame
    df = pd.DataFrame(data, columns=columns)
    
    # Load existing Excel file if it exists, or create new one
    try:
        with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    except FileNotFoundError:
        # If file doesn't exist, create it
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

def load_data_from_file(sheet_name):
    """Load data from Excel file"""
    data_dir = "data"
    excel_file = os.path.join(data_dir, "cpms_data.xlsx")
    
    if os.path.exists(excel_file):
        try:
            # Read the specific sheet
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            return df.values.tolist(), df.columns.tolist()
        except:
            return [], []
    return [], []

def save_current_data(selected):
    """Save current data for the selected sheet"""
    table_key = f"table_data_{selected}"
    col_key = f"table_cols_{selected}"
    if table_key in st.session_state and col_key in st.session_state:
        save_data_to_file(selected, st.session_state[table_key], st.session_state[col_key])

def delete_data_file(sheet_name):
    """Delete a specific sheet from the Excel file"""
    data_dir = "data"
    excel_file = os.path.join(data_dir, "cpms_data.xlsx")
    
    if os.path.exists(excel_file):
        try:
            # Read all sheets
            excel_data = pd.read_excel(excel_file, sheet_name=None)
            
            # Remove the specific sheet
            if sheet_name in excel_data:
                del excel_data[sheet_name]
                
                # Write back all remaining sheets
                with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
                    for sheet_name_remaining, df in excel_data.items():
                        df.to_excel(writer, sheet_name=sheet_name_remaining, index=False)
        except:
            pass

def get_excel_sheets():
    """Get list of available sheets in the Excel file"""
    data_dir = "data"
    excel_file = os.path.join(data_dir, "cpms_data.xlsx")
    
    if os.path.exists(excel_file):
        try:
            excel_data = pd.read_excel(excel_file, sheet_name=None)
            return [sheet for sheet in excel_data.keys() if sheet != 'Sheet1']
        except:
            return []
    return []

def show():
    st.markdown("""
        <style>
        .css-1d391kg .nav-link > span:first-child {
            display: none !important;
        }
        [data-testid="stSidebar"] .menu-title .menu-icon,
        [data-testid="stSidebar"] .menu-title svg {
            display: none !important;
        }
        /* Button hover color for Add/Delete buttons */
        .stButton>button:hover {
            background-color: #172087 !important;
            color: white !important;
        }
        /* Change the outline color on focus/active */
        .stButton>button:focus, .stButton>button:active {
            outline: 2px solid #172087 !important;
            box-shadow: 0 0 0 2px #17208733 !important;
        }

        /* Make table column headers bold and black */
        thead tr th {
            font-weight: bold !important;
            color: black !important;
        }
        </style>
    """, unsafe_allow_html=True)

    sheet_names = [
        "Dashboard",
        "Client", "Business Contact Information", "Business Registrations", "Business Owner",
        "Business Profile", "Business Financial Structure", "Market Domestic",
        "Market Export", "Market Import", "Product_Service Lines",
        "Employment Statistics", "Assistance", "Jobs Generated"
    ]

      # Modern Professional Sidebar with enhanced styling
    st.markdown("""
        <style>
        /* Modern Sidebar Design */
        .stSidebar {
            background: linear-gradient(180deg, #1e3a8a 0%, #172087 100%) !important;
            border-right: none !important;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1) !important;
        }
        
        /* Make all sidebar text white */
        .stSidebar * {
            color: white !important;
        }
        
        /* Sidebar titles and headers */
        .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar h4, .stSidebar h5, .stSidebar h6 {
            color: white !important;
        }
        
        /* Sidebar text elements */
        .stSidebar p, .stSidebar div, .stSidebar span, .stSidebar label {
            color: white !important;
        }
        
        /* Sidebar buttons text */
        .stSidebar button {
            color: white !important;
            background-color: rgba(255,255,255,0.1) !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            font-size: 13px !important;
            padding: 8px 12px !important;
            margin-bottom: 4px !important;
            height: auto !important;
            min-height: 35px !important;
            max-height: 35px !important;
        }
        
        /* Sidebar button hover */
        .stSidebar button:hover {
            background-color: rgba(255,255,255,0.2) !important;
            color: white !important;
        }
        
        /* Info boxes in sidebar */
        .stSidebar .stInfo {
            background-color: rgba(255,255,255,0.1) !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
        }
        
        .stSidebar .stInfo > div {
            color: white !important;
        }
        
        /* Custom header for sidebar */
        .sidebar-header {
            background: rgba(255,255,255,0.1);
            color: white;
            padding: 25px 20px;
            margin: 0;
            text-align: center;
            font-weight: 700;
            font-size: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
        }
        
        .sidebar-logo {
            width: 40px;
            height: 40px;
            background: white;
            border-radius: 50%;
            margin: 0 auto 15px auto;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            font-weight: bold;
            color: #172087;
        }
        
        /* Navigation Menu Styling */
        .nav-menu {
            padding: 20px 0;
        }
        
        .nav-item {
            display: flex;
            align-items: center;
            padding: 12px 20px;
            margin: 2px 10px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            color: rgba(255,255,255,0.8);
            font-size: 14px;
            font-weight: 500;
            text-decoration: none;
            border-left: 3px solid transparent;
        }
        
        .nav-item:hover {
            background: rgba(255,255,255,0.15);
            color: white;
            border-left: 3px solid #60a5fa;
            transform: translateX(5px);
        }
        
        .nav-item.active {
            background: rgba(255,255,255,0.2);
            color: white;
            border-left: 3px solid #60a5fa;
            font-weight: 600;
        }
        
        .nav-icon {
            margin-right: 12px;
            font-size: 16px;
            width: 20px;
            text-align: center;
        }
        
        /* Section dividers */
        .nav-section-title {
            color: rgba(255,255,255,0.6);
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 20px 20px 10px 20px;
            margin-top: 10px;
        }
        
        .nav-divider {
            height: 1px;
            background: rgba(255,255,255,0.1);
            margin: 15px 20px;
        }
        
        /* Data Management Section */
        .data-section {
            background: rgba(255,255,255,0.05);
            margin: 20px 10px;
            border-radius: 10px;
            padding: 15px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .data-section h4 {
            color: white;
            font-size: 14px;
            font-weight: 600;
            margin: 0 0 10px 0;
            display: flex;
            align-items: center;
        }
        
        .data-stats {
            color: rgba(255,255,255,0.8);
            font-size: 13px;
            margin-bottom: 15px;
        }
        
        /* Modern Buttons */
        .modern-btn {
            width: 100%;
            padding: 10px 15px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            margin-bottom: 8px;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .btn-danger {
            background: #ef4444;
            color: white;
        }
        
        .btn-danger:hover {
            background: #dc2626;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
        }
        
        .btn-secondary {
            background: #6b7280;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #4b5563;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(107, 114, 128, 0.3);
        }
        
        /* Hide default radio button styling */
        .stRadio > div {
            display: none !important;
        }
        
        /* Hide default sidebar elements */
        .css-1d391kg .nav-link > span:first-child {
            display: none !important;
        }
        
        [data-testid="stSidebar"] .menu-title .menu-icon,
        [data-testid="stSidebar"] .menu-title svg {
            display: none !important;
        }
        
        /* User info section */
        .user-info {
            position: absolute;
            bottom: 20px;
            left: 20px;
            right: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 15px;
            border: 1px solid rgba(255,255,255,0.2);
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
        
        .stSidebar .sidebar-content {
            padding: 0 !important;
        }
        </style>
     """, unsafe_allow_html=True)
    
    # Professional Sidebar using pure Streamlit components
    with st.sidebar:
        # Simple header
        st.title("CPMS Dashboard")
        
        # Define all menu items in order (no categories)
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
            "Product_Service Lines",
            "Employment Statistics",
            "Assistance",
            "Jobs Generated"
        ]
        
        # Initialize session state
        if "selected_nav_item" not in st.session_state:
            st.session_state.selected_nav_item = "Dashboard"
        
        # Create navigation without categories
        st.subheader("Navigation")
        
        for item in menu_items:
            # Create navigation buttons
            if st.button(item, key=f"nav_{item}", use_container_width=True):
                st.session_state.selected_nav_item = item
                st.rerun()
        
        selected = st.session_state.selected_nav_item
        
        # Data Management Section
        st.subheader("Data Management")
        
        data_dir = "data"
        excel_file = os.path.join(data_dir, "cpms_data.xlsx")
        if os.path.exists(excel_file):
            try:
                excel_data = pd.read_excel(excel_file, sheet_name=None)
                active_sheets = len([sheet for sheet in excel_data.keys() if sheet != 'Sheet1'])
                st.info(f"Active Sheets: {active_sheets}")
            except:
                st.info("Active Sheets: 0")
        else:
            st.info("Active Sheets: 0")
        
        # Action buttons
        st.subheader("Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Clear Data", key="clear_data_btn", type="secondary", use_container_width=True):
                if os.path.exists(excel_file):
                    os.remove(excel_file)
                st.success("All data cleared!")
                st.rerun()
        
        with col2:
            if st.button("Logout", key="logout_btn", type="primary", use_container_width=True):
                st.session_state["authenticated"] = False
                st.session_state["auth_cookie"] = None
                session_file = "session.json"
                if os.path.exists(session_file):
                    os.remove(session_file)
                st.rerun()
        
        # User info section
        st.divider()
        st.subheader("User Profile")
        
        auth_cookie = st.session_state.get("auth_cookie", {})
        user_name = auth_cookie.get("first_name", "User")
        user_last = auth_cookie.get("last_name", "")
        user_role = auth_cookie.get("role", "user")
        
        # Display user info using native components
        st.write(f"**Name:** {user_name} {user_last}")
        st.write(f"**Role:** {user_role.title()}")
    
    


    st.session_state.selected_sheet = selected

    # Update active sheets count in the custom sidebar
    data_dir = "data"
    excel_file = os.path.join(data_dir, "cpms_data.xlsx")
    active_sheets_count = 0
    if os.path.exists(excel_file):
        try:
            excel_data = pd.read_excel(excel_file, sheet_name=None)
            active_sheets_count = len([sheet for sheet in excel_data.keys() if sheet != 'Sheet1'])
        except:
            active_sheets_count = 0
    else:
        active_sheets_count = 0
    
    # Update the active sheets count in the sidebar via JavaScript
    st.markdown(f"""
        <script>
        updateActiveSheets({active_sheets_count});
        </script>
    """, unsafe_allow_html=True)

    # Add main content wrapper
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    st.markdown(f"<h3 style='font-weight: 600; color: #172087;'>{st.session_state.selected_sheet}</h3>", unsafe_allow_html=True)
    

    
    if selected == "Dashboard":
        st.markdown("Under Construction...")  # Placeholder for dashboard content
    
    elif selected == "Employment Statistics":
        st.markdown("Under Construction...")  # Placeholder for employment statistics content
    
    else:
        table_key = f"table_data_{selected}"
        col_key = f"table_cols_{selected}"

        # Set columns for every sheet
        if selected == "Client":
            columns = [
                "No",
                "Date Created (MM/DD/YYYY)",
                "Status of Client",
                "Category of Client",
                "Social Classification",
                "Client is Senior",
                "Client is Indigenous",
                "Level of Digitalization",
                "Client Designation",
                "First Name",
                "Last Name",
                "Civil Status",
                "Sex",
                "Barangay",
                "District",
                "Address",
                "Mobile Number",
                "Email Address"
            ]
        elif selected == "Business Contact Information":
            columns = [
                "No",
                "Status of Business Registration",
                "Region",
                "Province",
                "City/Municipality",
                "Barangay",
                "District",
                "Address",
                "Mobile Number",
                "Email Address"
            ]
        elif selected == "Business Registrations":
            columns = [
                "No",
                "Name of Business",
                "Registering Agency",
                "Agency Expiry Date (MM/DD/YYYY)",
                "Agency Reg Number"
            ]
        elif selected == "Business Owner":
            columns = [
                "No",
                "Given Name",
                "Last Name",
                "Civil Status",
                "Sex",
                "Citizenship",
                "Social Classification",
                "Owner is Senior",
                "Owner is Indigenous",
                "Region",
                "Province",
                "City/Municipality",
                "Barangay",
                "District",
                "Address"
            ]
        elif selected == "Business Profile":
            columns = [
                "No",
                "Year Established",
                "Form of Organization",
                "Major Activity",
                "Minor Activity",
                "PSIC Group",
                "PSIC Division",
                "PSIC Section",
                "Prio Industry Cluster"
            ]
        elif selected == "Business Financial Structure":
            columns = [
                "No",
                "Asset Classification Year",
                "Asset Size Range",
                "Sales History Year",
                "Domestic Sales"
            ]
        elif selected == "Market Domestic":
            columns = [
                "No",
                "Product/Service",
                "Region",
                "Province"
            ]
        elif selected == "Market Export":
            columns = [
                "No",
                "Year Export Started",
                "Product Service",
                "Country",
                "Trade Bloc"
            ]
        elif selected == "Market Import":
            columns = [
                "No",
                "Year Import Started",
                "Product Service",
                "Country"
            ]
        elif selected == "Product_Service Lines":
            columns = [
                "No",
                "Product/Service Line",
                "Major Raw Material/s"
            ]
        elif selected == "Assistance":
            columns = [
                "No",
                "EDT Assistance Level",
                "Type of Assistance",
                "Sub Type of Asisstance",
                "Remarks",
                "Date Start (MM/DD/YYYY)",
                "Date End (MM/DD/YYYY)",
                "MSME Program",
                "MSME Availed (MM/DD/YYYY)",
                "Assisted By",
                "Assisting Office",
                "Assisting Officer Region",
                "Assisting Officer Province",
                "Assisting Officer City"
            ]
        elif selected == "Jobs Generated":
            columns = [
                "No",
                "Date Recorded (MM/DD/YYYY)",
                "Direct Community Jobs",
                "Direct Home Based",
                "Indirect Home Based",
                "Direct Jobs Sustained"
            ]
        else:
            columns = [f"Column {i+1}" for i in range(5)]

        # Always update session state for columns
        st.session_state[col_key] = columns

        # Load data from persistent storage or initialize if not exists
        if table_key not in st.session_state:
            saved_data, saved_columns = load_data_from_file(selected)
            if saved_data:
                st.session_state[table_key] = saved_data
                st.session_state[col_key] = saved_columns
            else:
                # Initialize with empty data if no saved data exists
                st.session_state[table_key] = []
                st.session_state[col_key] = columns
        if col_key not in st.session_state:
            st.session_state[col_key] = columns

        data = st.session_state[table_key]
        columns = st.session_state[col_key]

        # Convert to DataFrame for editing (force all data to string for editable headers)
        df = pd.DataFrame(data, columns=columns)
        df = df.astype(str)  # Make all cells text for compatibility

        # Build column config for editable column titles (all as TextColumn)
        column_config = {
            col: st.column_config.TextColumn(label=col, required=True)
            for col in df.columns
        }

        # --- NEW: Add Entry Button and Form with Close (x) Button ---
        form_state_key = f"show_add_entry_form_{selected}"
        if form_state_key not in st.session_state:
            st.session_state[form_state_key] = False

        # Add Entry Button
        st.markdown("### Data Entry")
        if st.button("Add Entry", key=f"add_entry_btn_{selected}"):
            st.session_state[form_state_key] = True
            st.rerun()

        if st.session_state[form_state_key]:
            if selected == "Business Contact Information":
                st.markdown("#### Step 1: Fill out the form")
                
                # Initialize session state for success message
                if 'bci_show_success' not in st.session_state:
                    st.session_state.bci_show_success = False
                    st.session_state.bci_success_timer = 0
                
                # Simple input fields without forms
                st.markdown(f"### Add Entry to {selected}")
                new_entry = {}
                
                # Row 1: Status of Business Registration
                new_entry["Status of Business Registration"] = st.selectbox(
                    "Status of Business Registration",
                    ["Registered", "Unregistered"],
                    key=f"bci_status_{st.session_state.get('bci_form_counter', 0)}"
                )
                
                # Row 2: Mobile Number and Email Address
                col1, col2 = st.columns(2)
                with col1:
                    new_entry["Mobile Number"] = st.text_input("Mobile Number", key=f"bci_mobile_{st.session_state.get('bci_form_counter', 0)}")
                with col2:
                    new_entry["Email Address"] = st.text_input("Email Address", key=f"bci_email_{st.session_state.get('bci_form_counter', 0)}")
                
                # Location Information
                st.markdown("#### Location Information")
                location_data = create_location_widgets()
                new_entry["Region"] = location_data["region"]
                new_entry["Province"] = location_data["province"]
                new_entry["City/Municipality"] = location_data["city"]
                new_entry["Barangay"] = location_data["barangay"]
                new_entry["Purok"] = location_data["purok"]
                
                # Address Information
                st.markdown("#### Address Information")
                new_entry["District"] = st.text_input("District", key=f"bci_district_{st.session_state.get('bci_form_counter', 0)}")
                new_entry["Address"] = st.text_input("Address", key=f"bci_address_{st.session_state.get('bci_form_counter', 0)}")
                new_entry["Zip Code"] = st.text_input("Zip Code", key=f"bci_zip_code_{st.session_state.get('bci_form_counter', 0)}")
                
                # Submit button
                submitted = st.button("Submit")
                
                if submitted:
                    # Auto-increment 'No' and ensure order
                    data = st.session_state[table_key]
                    next_no = len(data) + 1
                    row = [str(next_no)]
                    for col in columns[1:]:
                        row.append(new_entry.get(col, ""))
                    df.loc[len(df)] = row
                    # Sort by 'No' just in case
                    df["No"] = df["No"].astype(int)
                    df = df.sort_values("No").reset_index(drop=True)
                    df["No"] = df.index + 1
                    st.session_state[table_key] = df.values.tolist()
                    save_current_data(selected)
                    
                    # Set success message flag
                    st.session_state.bci_show_success = True
                    # Clear location dropdowns
                    st.session_state.loc_region = None
                    st.session_state.loc_province = None
                    st.session_state.loc_city = None
                    st.session_state.loc_barangay = None
                    # Clear form fields by incrementing counter
                    if 'bci_form_counter' not in st.session_state:
                        st.session_state.bci_form_counter = 0
                    st.session_state.bci_form_counter += 1
                    st.rerun()
                
                # Show success message if flag is set
                if st.session_state.bci_show_success:
                    st.success("Input saved, thank you!")
                    # Auto-hide after 3 seconds using a counter
                    if 'bci_success_timer' not in st.session_state:
                        st.session_state.bci_success_timer = 0
                    st.session_state.bci_success_timer += 1
                    if st.session_state.bci_success_timer >= 30:  # ~3 seconds
                        st.session_state.bci_show_success = False
                        st.session_state.bci_success_timer = 0
            elif selected == "Business Registrations":
                # Initialize session state for success message
                if 'br_show_success' not in st.session_state:
                    st.session_state.br_show_success = False
                    st.session_state.br_success_timer = 0
                
                # Simple input fields without forms
                st.markdown(f"### Add Entry to {selected}")
                new_entry = {}
                
                # Row 1: Name of Business (full width)
                name_business = st.text_input("Name of Business", key=f"br_name_{st.session_state.get('br_form_counter', 0)}")
                name_business_upper = name_business.upper()
                st.write(f"**Preview:** {name_business_upper}")
                new_entry["Name of Business"] = name_business_upper
                
                # Row 2: Registering Agency and Agency Reg Number
                col1, col2 = st.columns(2)
                with col1:
                    new_entry["Registering Agency"] = st.selectbox(
                        "Registering Agency",
                        ["CDA", "DOLE", "DTI", "SEC"],
                        key=f"br_agency_{st.session_state.get('br_form_counter', 0)}"
                    )
                with col2:
                    agency_reg_number = st.text_input("Agency Reg Number", key=f"br_reg_number_{st.session_state.get('br_form_counter', 0)}")
                    new_entry["Agency Reg Number"] = agency_reg_number
                
                # Row 3: Agency Expiry Date
                expiry_col = [col for col in columns if "Agency Expiry Date" in col][0] if any("Agency Expiry Date" in col for col in columns) else "Agency Expiry Date (MM/DD/YYYY)"
                agency_expiry_date = st.date_input("Agency Expiry Date", key=f"br_expiry_{st.session_state.get('br_form_counter', 0)}")
                new_entry[expiry_col] = agency_expiry_date.strftime("%m/%d/%Y")
                
                # Submit button
                submitted = st.button("Submit")
                
                if submitted:
                    if not agency_reg_number.isdigit():
                        st.warning("Agency Reg Number must only contain numbers.")
                    else:
                        # Auto-increment 'No' and ensure order
                        data = st.session_state[table_key]
                        next_no = len(data) + 1
                        row = [str(next_no)]
                        for col in columns[1:]:
                            row.append(new_entry.get(col, ""))
                        df.loc[len(df)] = row
                        # Sort by 'No' just in case
                        df["No"] = df["No"].astype(int)
                        df = df.sort_values("No").reset_index(drop=True)
                        df["No"] = df.index + 1
                        st.session_state[table_key] = df.values.tolist()
                        save_current_data(selected)
                        
                        # Set success message flag
                        st.session_state.br_show_success = True
                        # Clear form fields by incrementing counter
                        if 'br_form_counter' not in st.session_state:
                            st.session_state.br_form_counter = 0
                        st.session_state.br_form_counter += 1
                        st.rerun()
                
                # Show success message if flag is set
                if st.session_state.br_show_success:
                    st.success("Input saved, thank you!")
                    # Auto-hide after 3 seconds using a counter
                    if 'br_success_timer' not in st.session_state:
                        st.session_state.br_success_timer = 0
                    st.session_state.br_success_timer += 1
                    if st.session_state.br_success_timer >= 30:  # ~3 seconds
                        st.session_state.br_show_success = False
                        st.session_state.br_success_timer = 0
            elif selected == "Business Owner":
                # Citizenship list (ISO country names, sorted)
                citizenships = [
                    'Afghan', 'Albanian', 'Algerian', 'American', 'Andorran', 'Angolan', 'Antiguans', 'Argentinean', 'Armenian', 'Australian', 'Austrian', 'Azerbaijani',
                    'Bahamian', 'Bahraini', 'Bangladeshi', 'Barbadian', 'Barbudans', 'Batswana', 'Belarusian', 'Belgian', 'Belizean', 'Beninese', 'Bhutanese', 'Bolivian',
                    'Bosnian', 'Brazilian', 'British', 'Bruneian', 'Bulgarian', 'Burkinabe', 'Burmese', 'Burundian', 'Cambodian', 'Cameroonian', 'Canadian', 'Cape Verdean',
                    'Central African', 'Chadian', 'Chilean', 'Chinese', 'Colombian', 'Comoran', 'Congolese', 'Costa Rican', 'Croatian', 'Cuban', 'Cypriot', 'Czech',
                    'Danish', 'Djibouti', 'Dominican', 'Dutch', 'East Timorese', 'Ecuadorean', 'Egyptian', 'Emirian', 'Equatorial Guinean', 'Eritrean', 'Estonian', 'Ethiopian',
                    'Fijian', 'Filipino', 'Finnish', 'French', 'Gabonese', 'Gambian', 'Georgian', 'German', 'Ghanaian', 'Greek', 'Grenadian', 'Guatemalan', 'Guinea-Bissauan',
                    'Guinean', 'Guyanese', 'Haitian', 'Herzegovinian', 'Honduran', 'Hungarian', 'I-Kiribati', 'Icelander', 'Indian', 'Indonesian', 'Iranian', 'Iraqi',
                    'Irish', 'Israeli', 'Italian', 'Ivorian', 'Jamaican', 'Japanese', 'Jordanian', 'Kazakhstani', 'Kenyan', 'Kittian and Nevisian', 'Kuwaiti', 'Kyrgyz',
                    'Laotian', 'Latvian', 'Lebanese', 'Liberian', 'Libyan', 'Liechtensteiner', 'Lithuanian', 'Luxembourger', 'Macedonian', 'Malagasy', 'Malawian', 'Malaysian',
                    'Maldivan', 'Malian', 'Maltese', 'Marshallese', 'Mauritanian', 'Mauritian', 'Mexican', 'Micronesian', 'Moldovan', 'Monacan', 'Mongolian', 'Moroccan',
                    'Mosotho', 'Motswana', 'Mozambican', 'Namibian', 'Nauruan', 'Nepalese', 'New Zealander', 'Nicaraguan', 'Nigerian', 'Nigerien', 'North Korean',
                    'Northern Irish', 'Norwegian', 'Omani', 'Pakistani', 'Palauan', 'Panamanian', 'Papua New Guinean', 'Paraguayan', 'Peruvian', 'Polish', 'Portuguese',
                    'Qatari', 'Romanian', 'Russian', 'Rwandan', 'Saint Lucian', 'Salvadoran', 'Samoan', 'San Marinese', 'Sao Tomean', 'Saudi', 'Scottish', 'Senegalese',
                    'Serbian', 'Seychellois', 'Sierra Leonean', 'Singaporean', 'Slovakian', 'Slovenian', 'Solomon Islander', 'Somali', 'South African', 'South Korean',
                    'Spanish', 'Sri Lankan', 'Sudanese', 'Surinamer', 'Swazi', 'Swedish', 'Swiss', 'Syrian', 'Taiwanese', 'Tajik', 'Tanzanian', 'Thai', 'Togolese',
                    'Tongan', 'Trinidadian or Tobagonian', 'Tunisian', 'Turkish', 'Tuvaluan', 'Ugandan', 'Ukrainian', 'Uruguayan', 'Uzbekistani', 'Venezuelan', 'Vietnamese',
                    'Welsh', 'Yemenite', 'Zambian', 'Zimbabwean'
                ]
                citizenships = sorted(citizenships)
                
                # Simple input fields without forms
                st.markdown(f"### Add Entry to {selected}")
                new_entry = {}
                
                # Personal Information
                st.markdown("#### Personal Information")
                
                # Row 1: Given Name and Last Name
                col1, col2 = st.columns(2)
                with col1:
                    new_entry["Given Name"] = st.text_input("Given Name", key=f"bo_given_name_{st.session_state.get('bo_form_counter', 0)}")
                with col2:
                    new_entry["Last Name"] = st.text_input("Last Name", key=f"bo_last_name_{st.session_state.get('bo_form_counter', 0)}")
                
                # Row 2: Civil Status and Sex
                col1, col2 = st.columns(2)
                with col1:
                    new_entry["Civil Status"] = st.text_input("Civil Status", key=f"bo_civil_status_{st.session_state.get('bo_form_counter', 0)}")
                with col2:
                    new_entry["Sex"] = st.text_input("Sex", key=f"bo_sex_{st.session_state.get('bo_form_counter', 0)}")
                
                # Row 3: Citizenship and Social Classification
                col1, col2 = st.columns(2)
                with col1:
                    new_entry["Citizenship"] = st.selectbox("Citizenship", citizenships, key=f"bo_citizenship_{st.session_state.get('bo_form_counter', 0)}")
                with col2:
                    new_entry["Social Classification"] = st.selectbox(
                        "Social Classification",
                        ["Abled", "Person with Disabilities"],
                        key=f"bo_social_class_{st.session_state.get('bo_form_counter', 0)}"
                    )
                
                # Row 4: Senior and Indigenous
                col1, col2 = st.columns(2)
                with col1:
                    new_entry["Owner is Senior"] = st.selectbox(
                        "Owner is Senior",
                        ["Yes", "No"],
                        key=f"bo_senior_{st.session_state.get('bo_form_counter', 0)}"
                    )
                with col2:
                    new_entry["Owner is Indigenous"] = st.selectbox(
                        "Owner is Indigenous",
                        ["Yes", "No"],
                        key=f"bo_indigenous_{st.session_state.get('bo_form_counter', 0)}"
                    )
                
                # Location Information
                st.markdown("#### Location Information")
                location_data = create_location_widgets()
                new_entry["Region"] = location_data["region"]
                new_entry["Province"] = location_data["province"]
                new_entry["City/Municipality"] = location_data["city"]
                new_entry["Barangay"] = location_data["barangay"]
                new_entry["Purok"] = location_data["purok"]
                
                # Address Information
                st.markdown("#### Address Information")
                new_entry["District"] = st.text_input("District")
                new_entry["Address"] = st.text_input("Address")
                new_entry["Zip Code"] = st.text_input("Zip Code")
                
                # Submit button
                submitted = st.button("Submit")
                
                if submitted:
                    # Auto-increment 'No' and ensure order
                    data = st.session_state[table_key]
                    next_no = len(data) + 1
                    row = [str(next_no)]
                    for col in columns[1:]:
                        row.append(new_entry.get(col, ""))
                    df.loc[len(df)] = row
                    # Sort by 'No' just in case
                    df["No"] = df["No"].astype(int)
                    df = df.sort_values("No").reset_index(drop=True)
                    df["No"] = df.index + 1
                    st.session_state[table_key] = df.values.tolist()
                    save_current_data(selected)
                    
                    # Set success message flag
                    st.session_state.bo_show_success = True
                    # Increment counter to clear text inputs
                    st.session_state.bo_form_counter = st.session_state.get('bo_form_counter', 0) + 1
                    # Clear location dropdowns
                    st.session_state.loc_region = None
                    st.session_state.loc_province = None
                    st.session_state.loc_city = None
                    st.session_state.loc_barangay = None
                    st.rerun()
                
                # Show success message if flag is set
                if st.session_state.get('bo_show_success', False):
                    st.success("Input saved, thank you!")
                    # Auto-hide after 3 seconds using a counter
                    if 'bo_success_timer' not in st.session_state:
                        st.session_state.bo_success_timer = 0
                    st.session_state.bo_success_timer += 1
                    if st.session_state.bo_success_timer >= 30:  # ~3 seconds
                        st.session_state.bo_show_success = False
                        st.session_state.bo_success_timer = 0
            elif selected == "Business Profile":
                # Major Activity options
                activity_options = [
                    "Manufacturing/Producing", "Retailing/Trading", "Wholesaling/Trading", "Service", "Exporting", "Importing"
                ]
                # PSIC Section mapping by Major Activity
                psic_section_map = {
                    "Manufacturing/Producing": [
                        "Section C: Manufacturing",
                        "Section A: Agriculture, Forestry and Fishing (primary production)",
                        "Section B: Mining and Quarrying",
                        "Section D: Electricity, Gas, Steam, and Air Conditioning Supply",
                        "Section E: Water Supply; Sewerage, Waste Management and Remediation Activities",
                        "Section F: Construction (producing physical structures)"
                    ],
                    "Retailing/Trading": [
                        "Section G: Wholesale and Retail Trade; Repair of Motor Vehicles and Motorcycles"
                    ],
                    "Wholesaling/Trading": [
                        "Section G: Wholesale and Retail Trade; Repair of Motor Vehicles and Motorcycles"
                    ],
                    "Service": [
                        "Section I: Accommodation and Food Service Activities",
                        "Section J: Information and Communication",
                        "Section K: Financial and Insurance Activities",
                        "Section L: Real Estate Activities",
                        "Section M: Professional, Scientific and Technical Activities",
                        "Section N: Administrative and Support Service Activities",
                        "Section O: Public Administration and Defense; Compulsory Social Security",
                        "Section P: Education",
                        "Section Q: Human Health and Social Work Activities",
                        "Section R: Arts, Entertainment and Recreation",
                        "Section S: Other Service Activities",
                        "Section T: Activities of Households as Employers; Undifferentiated Goods- and Services-Producing Activities of Households for Own Use"
                    ],
                    "Exporting": [
                        "Section A: Agriculture, Forestry and Fishing",
                        "Section B: Mining and Quarrying",
                        "Section C: Manufacturing",
                        "Section G: Wholesale and Retail Trade; Repair of Motor Vehicles and Motorcycles (especially wholesale)",
                        "Section H: Transportation and Storage (logistics for imports/exports)"
                    ],
                    "Importing": [
                        "Section A: Agriculture, Forestry and Fishing",
                        "Section B: Mining and Quarrying",
                        "Section C: Manufacturing",
                        "Section G: Wholesale and Retail Trade; Repair of Motor Vehicles and Motorcycles (especially wholesale)",
                        "Section H: Transportation and Storage (logistics for imports/exports)"
                    ]
                }
                # PSIC Division mapping by PSIC Section (user's list)
                psic_division_map = {
                    "Section A: Agriculture, Forestry and Fishing": [
                        "01 - Crop and animal production, hunting, and related service activities",
                        "02 - Forestry and logging",
                        "03 - Fishing and aquaculture"
                    ],
                    "Section B: Mining and Quarrying": [
                        "05 - Mining of coal and lignite",
                        "06 - Extraction of crude petroleum and natural gas",
                        "07 - Mining of metal ores",
                        "08 - Other mining and quarrying",
                        "09 - Mining support service activities"
                    ],
                    "Section C: Manufacturing": [
                        "10 - Manufacture of food products",
                        "11 - Manufacture of beverages",
                        "12 - Manufacture of tobacco products",
                        "13 - Manufacture of textiles",
                        "14 - Manufacture of wearing apparel",
                        "15 - Manufacture of leather and related products",
                        "16 - Manufacture of wood and wood products (excluding furniture)",
                        "17 - Manufacture of paper and paper products",
                        "18 - Printing and reproduction of recorded media",
                        "19 - Manufacture of coke and refined petroleum products",
                        "20 - Manufacture of chemicals and chemical products",
                        "21 - Manufacture of pharmaceutical and medicinal products",
                        "22 - Manufacture of rubber and plastics products",
                        "23 - Manufacture of other non-metallic mineral products",
                        "24 - Manufacture of basic metals",
                        "25 - Manufacture of fabricated metal products (excluding machinery)",
                        "26 - Manufacture of computer, electronic, and optical products",
                        "27 - Manufacture of electrical equipment",
                        "28 - Manufacture of machinery and equipment n.e.c.",
                        "29 - Manufacture of motor vehicles, trailers, and semi-trailers",
                        "30 - Manufacture of other transport equipment",
                        "31 - Manufacture of furniture",
                        "32 - Other manufacturing",
                        "33 - Repair and installation of machinery and equipment"
                    ],
                    "Section D: Electricity, Gas, Steam, and Air Conditioning Supply": [
                        "35 - Electricity, gas, steam, and air conditioning supply (including generation, transmission, and distribution)"
                    ],
                    "Section E: Water Supply; Sewerage, Waste Management and Remediation Activities": [
                        "36 - Water collection, treatment, and supply",
                        "37 - Sewerage",
                        "38 - Waste collection, treatment, and disposal; materials recovery",
                        "39 - Remediation activities and other waste management services"
                    ],
                    "Section F: Construction": [
                        "41 - Construction of buildings",
                        "42 - Civil engineering",
                        "43 - Specialized construction activities"
                    ],
                    "Section G: Wholesale and Retail Trade; Repair of Motor Vehicles and Motorcycles": [
                        "45 - Wholesale and retail trade; repair of motor vehicles and motorcycles",
                        "46 - Wholesale trade (excluding vehicles and motorcycles)",
                        "47 - Retail trade (excluding vehicles and motorcycles)"
                    ],
                    "Section H: Transportation and Storage": [
                        "49 - Land transport and transport via pipelines",
                        "50 - Water transport",
                        "51 - Air transport",
                        "52 - Warehousing and support activities for transportation",
                        "53 - Postal and courier activities"
                    ],
                    "Section I: Accommodation and Food Service Activities": [
                        "55 - Accommodation",
                        "56 - Food and beverage service activities"
                    ],
                    "Section J: Information and Communication": [
                        "58 - Publishing activities",
                        "59 - Motion picture, video, and television program production",
                        "60 - Programming and broadcasting activities",
                        "61 - Telecommunications",
                        "62 - Computer programming, consultancy and related activities",
                        "63 - Information service activities"
                    ],
                    "Section K: Financial and Insurance Activities": [
                        "64 - Financial service activities (excluding insurance and pension funding)",
                        "65 - Insurance, reinsurance and pension funding (excluding compulsory social security)",
                        "66 - Auxiliary activities for financial services and insurance"
                    ],
                    "Section L: Real Estate Activities": [
                        "68 - Real estate activities"
                    ],
                    "Section M: Professional, Scientific and Technical Activities": [
                        "69 - Legal and accounting activities",
                        "70 - Activities of head offices; management consultancy",
                        "71 - Architectural and engineering; technical testing and analysis",
                        "72 - Scientific research and development",
                        "73 - Advertising and market research",
                        "74 - Other professional, scientific and technical activities",
                        "75 - Veterinary activities"
                    ],
                    "Section N: Administrative and Support Service Activities": [
                        "77 - Rental and leasing activities",
                        "78 - Employment activities",
                        "79 - Travel agency, tour operator, and related reservation services",
                        "80 - Security and investigation activities",
                        "81 - Services to buildings and landscape activities",
                        "82 - Office administrative, support, and other business support activities"
                    ],
                    "Section O: Public Administration and Defense; Compulsory Social Security": [
                        "84 - Public administration and defense; compulsory social security"
                    ],
                    "Section P: Education": [
                        "85 - Education"
                    ],
                    "Section Q: Human Health and Social Work Activities": [
                        "86 - Human health activities",
                        "87 - Residential care activities",
                        "88 - Social work activities without accommodation"
                    ],
                    "Section R: Arts, Entertainment and Recreation": [
                        "90 - Creative, arts and entertainment activities",
                        "91 - Libraries, archives, museums ,and other cultural activities",
                        "92 - Gambling and betting activities",
                        "93 - Sports activities and amusement,t and recreation activities"
                    ],
                    "Section S: Other Service Activities": [
                        "94 - Activities of membership organizations",
                        "95 - Repair of computers, personal and household goods",
                        "96 - Other personal service activities"
                    ],
                    "Section T: Activities of Households as Employers; Undifferentiated Goods- and Services-Producing Activities of Households for Own Use": [
                        "97 - Activities of households as employers of domestic personnel",
                        "98 - Undifferentiated goods‑ and services‑producing activities of private households for own use"
                    ]
                }
                # PSIC Group mapping by PSIC Division (user's batch 1)
                psic_group_map = {
                    "01 - Crop and animal production, hunting, and related service activities": [
                        "011 - Growing of non-perennial crops",
                        "012 - Growing of perennial crops",
                        "013 - Plant propagation",
                        "014 - Animal production",
                        "015 - Mixed farming",
                        "016 - Support activities to agriculture and post-harvest crop activities",
                        "017 - Hunting, trapping, and related service activities"
                    ],
                    "02 - Forestry and logging": [
                        "021 - Silviculture and other forestry activities",
                        "022 - Logging",
                        "023 - Gathering of non-wood forest products",
                        "024 - Support services to forestry"
                    ],
                    "03 - Fishing and aquaculture": [
                        "031 - Fishing",
                        "032 - Aquaculture"
                    ],
                    "05 - Mining of coal and lignite": [
                        "051 - Mining of hard coal",
                        "052 - Mining of lignite"
                    ],
                    "06 - Extraction of crude petroleum and natural gas": [
                        "061 - Extraction of crude petroleum",
                        "062 - Extraction of natural gas"
                    ],
                    "07 - Mining of metal ores": [
                        "071 - Mining of iron ores",
                        "072 - Mining of non-ferrous metal ores"
                    ],
                    "08 - Other mining and quarrying": [
                        "081 - Quarrying of stone, sand, and clay",
                        "089 - Mining and quarrying n.e.c. (not elsewhere classified)"
                    ],
                    "09 - Mining support service activities": [
                        "091 - Support activities for petroleum and natural gas extraction",
                        "099 - Support activities for other mining and quarrying"
                    ],
                    "10 - Manufacture of food products": [
                        "101 - Processing and preserving of meat",
                        "102 - Processing and preserving of fish, crustaceans, and mollusks",
                        "103 - Processing and preserving of fruit and vegetables",
                        "104 - Manufacture of vegetable and animal oils and fats",
                        "105 - Manufacture of dairy products",
                        "106 - Manufacture of grain mill products, starches, and starch products",
                        "107 - Manufacture of other food products",
                        "108 - Manufacture of prepared animal feeds"
                    ],
                    "11 - Manufacture of beverages": [
                        "110 - Manufacture of beverages"
                    ],
                    "12 - Manufacture of tobacco products": [
                        "120 - Manufacture of tobacco products"
                    ],
                    "13 - Manufacture of textiles": [
                        "131 - Spinning, weaving, and finishing of textiles",
                        "139 - Manufacture of other textiles"
                    ],
                    "14 - Manufacture of wearing apparel": [
                        "141 - Manufacture of wearing apparel, except fur apparel",
                        "142 - Manufacture of articles of fur",
                        "143 - Manufacture of knitted and crocheted apparel"
                    ],
                    "15 - Manufacture of leather and related products": [
                        "151 - Tanning and dressing of leather; manufacture of luggage, handbags, saddlery, and harness",
                        "152 - Manufacture of footwear"
                    ],
                    "16 - Manufacture of wood and wood products (excluding furniture)": [
                        "161 - Sawmilling and planing of wood",
                        "162 - Manufacture of products of wood, cork, straw, and plaiting materials (excluding furniture)"
                    ],
                    "17 - Manufacture of paper and paper products": [
                        "170 - Manufacture of paper and paper products"
                    ],
                    "18 - Printing and reproduction of recorded media": [
                        "181 - Printing",
                        "182 - Reproduction of recorded media"
                    ],
                    "19 - Manufacture of coke and refined petroleum products": [
                        "191 - Manufacture of coke oven products",
                        "192 - Manufacture of refined petroleum products"
                    ],
                    "20 - Manufacture of chemicals and chemical products": [
                        "201 - Manufacture of basic chemicals, fertilizers and nitrogen compounds, plastics and synthetic rubber in primary forms",
                        "202 - Manufacture of other chemical products",
                        "203 - Manufacture of man-made fibers"
                    ],
                    "21 - Manufacture of pharmaceutical and medicinal products": [
                        "210 - Manufacture of pharmaceuticals, medicinal chemical and botanical products"
                    ],
                    "22 - Manufacture of rubber and plastics products": [
                        "221 - Manufacture of rubber products",
                        "222 - Manufacture of plastics products"
                    ],
                    "23 - Manufacture of other non-metallic mineral products": [
                        "231 - Manufacture of glass and glass products",
                        "239 - Manufacture of non-metallic mineral products n.e.c."
                    ],
                    "24 - Manufacture of basic metals": [
                        "241 - Manufacture of basic iron and steel",
                        "242 - Manufacture of basic precious and other non-ferrous metals",
                        "243 - Casting of metals"
                    ],
                    "25 - Manufacture of fabricated metal products (excluding machinery)": [
                        "251 - Manufacture of structural metal products, tanks, reservoirs and steam generators",
                        "259 - Manufacture of other fabricated metal products; metalworking service activities"
                    ],
                    "26 - Manufacture of computer, electronic, and optical products": [
                        "261 - Manufacture of electronic components and boards",
                        "262 - Manufacture of computers and peripheral equipment",
                        "263 - Manufacture of communication equipment",
                        "264 - Manufacture of consumer electronics",
                        "265 - Manufacture of measuring, testing, navigating and control equipment; watches and clocks",
                        "266 - Manufacture of irradiation, electromedical and electrotherapeutic equipment",
                        "267 - Manufacture of optical instruments and photographic equipment",
                        "268 - Manufacture of magnetic and optical media"
                    ],
                    "27 - Manufacture of electrical equipment": [
                        "271 - Manufacture of electric motors, generators, transformers and electricity distribution and control apparatus",
                        "272 - Manufacture of batteries and accumulators",
                        "273 - Manufacture of wiring and wiring devices",
                        "274 - Manufacture of electric lighting equipment",
                        "275 - Manufacture of domestic appliances",
                        "279 - Manufacture of other electrical equipment"
                    ],
                    "28 - Manufacture of machinery and equipment n.e.c.": [
                        "281 - Manufacture of general-purpose machinery",
                        "282 - Manufacture of special-purpose machinery"
                    ],
                    "29 - Manufacture of motor vehicles, trailers, and semi-trailers": [
                        "291 - Manufacture of motor vehicles",
                        "292 - Manufacture of bodies (coachwork) for motor vehicles; manufacture of trailers and semi-trailers",
                        "293 - Manufacture of parts and accessories for motor vehicles"
                    ],
                    "30 - Manufacture of other transport equipment": [
                        "301 - Building of ships and boats",
                        "302 - Manufacture of railway locomotives and rolling stock",
                        "303 - Manufacture of air and spacecraft and related machinery",
                        "304 - Manufacture of military fighting vehicles",
                        "309 - Manufacture of transport equipment n.e.c."
                    ],
                    "31 - Manufacture of furniture": [
                        "310 - Manufacture of furniture"
                    ],
                    "32 - Other manufacturing": [
                        "321 - Manufacture of jewelry, bijouterie and related articles",
                        "322 - Manufacture of musical instruments",
                        "323 - Manufacture of sports goods",
                        "324 - Manufacture of games and toys",
                        "325 - Manufacture of medical and dental instruments and supplies",
                        "329 - Other manufacturing n.e.c."
                    ],
                    "33 - Repair and installation of machinery and equipment": [
                        "331 - Repair of fabricated metal products",
                        "332 - Repair of machinery",
                        "333 - Repair of electronic and optical equipment"
                    ],
                    "35 - Electricity, gas, steam, and air conditioning supply (including generation, transmission, and distribution)": [
                        "351 - Electric power generation, transmission and distribution",
                        "352 - Manufacture of gas; distribution of gaseous fuels through mains",
                        "353 - Steam and air conditioning supply"
                    ],
                    "36 - Water collection, treatment, and supply": [
                        "360 - Water collection, treatment and supply"
                    ],
                    "37 - Sewerage": [
                        "370 - Sewerage"
                    ],
                    "38 - Waste collection, treatment, and disposal; materials recovery": [
                        "381 - Waste collection",
                        "382 - Waste treatment and disposal",
                        "383 - Materials recovery"
                    ],
                    "39 - Remediation activities and other waste management services": [
                        "390 - Remediation activities and other waste management services"
                    ],
                    "41 - Construction of buildings": [
                        "410 - Construction of buildings"
                    ],
                    "42 - Civil engineering": [
                        "421 - Construction of roads and railways",
                        "422 - Construction of utility projects",
                        "429 - Construction of other civil engineering projects"
                    ],
                    "43 - Specialized construction activities": [
                        "431 - Demolition and site preparation",
                        "432 - Electrical, plumbing and other construction installation activities",
                        "433 - Building completion and finishing",
                        "439 - Other specialized construction activities"
                    ],
                    "45 - Wholesale and retail trade; repair of motor vehicles and motorcycles": [
                        "451 - Sale of motor vehicles",
                        "452 - Maintenance and repair of motor vehicles",
                        "453 - Sale of motor vehicle parts and accessories",
                        "454 - Sale, maintenance and repair of motorcycles and related parts and accessories"
                    ],
                    "46 - Wholesale trade (excluding vehicles and motorcycles)": [
                        "461 - Wholesale on a fee or contract basis",
                        "462 - Wholesale of agricultural raw materials and live animals",
                        "463 - Wholesale of food, beverages and tobacco",
                        "464 - Wholesale of household goods",
                        "465 - Wholesale of machinery, equipment and supplies",
                        "466 - Other specialized wholesale",
                        "469 - Non-specialized wholesale trade"
                    ],
                    "47 - Retail trade (excluding vehicles and motorcycles)": [
                        "471 - Retail sale in non-specialized stores",
                        "472 - Retail sale of food, beverages and tobacco in specialized stores",
                        "473 - Retail sale of automotive fuel in specialized stores",
                        "474 - Retail sale of information and communications equipment in specialized stores",
                        "475 - Retail sale of other household equipment in specialized stores",
                        "476 - Retail sale of cultural and recreation goods in specialized stores",
                        "477 - Retail sale of other goods in specialized stores",
                        "478 - Retail sale via stalls and markets",
                        "479 - Retail trade not in stores, stalls or markets (e.g., online selling, door-to-door)"
                    ],
                    "49 - Land transport and transport via pipelines": [
                        "491 - Transport via railways",
                        "492 - Other land transport",
                        "493 - Transport via pipelines"
                    ],
                    "50 - Water transport": [
                        "501 - Sea and coastal water transport",
                        "502 - Inland water transport"
                    ],
                    "51 - Air transport": [
                        "511 - Passenger air transport",
                        "512 - Freight air transport"
                    ],
                    "52 - Warehousing and support activities for transportation": [
                        "521 - Warehousing and storage",
                        "522 - Support activities for transportation"
                    ],
                    "53 - Postal and courier activities": [
                        "531 - Postal activities",
                        "532 - Courier activities"
                    ],
                    "55 - Accommodation": [
                        "551 - Short term accommodation activities",
                        "552 - Camping grounds, recreational vehicle parks and trailer parks",
                        "559 - Other accommodation"
                    ],
                    "56 - Food and beverage service activities": [
                        "561 - Restaurants and mobile food service activities",
                        "562 - Event catering and other food service activities",
                        "563 - Beverage serving activities"
                    ],
                    "58 - Publishing activities": [
                        "581 - Publishing of books, periodicals and other publishing activities",
                        "582 - Software publishing"
                    ],
                    "59 - Motion picture, video, and television program production": [
                        "591 - Motion picture, video and television program activities",
                        "592 - Sound recording and music publishing activities"
                    ],
                    "60 - Programming and broadcasting activities": [
                        "601 - Radio broadcasting",
                        "602 - Television programming and broadcasting activities"
                    ],
                    "61 - Telecommunications": [
                        "611 - Wired telecommunications activities",
                        "612 - Wireless telecommunications activities",
                        "613 - Satellite telecommunications activities",
                        "619 - Other telecommunications activities"
                    ],
                    "62 - Computer programming, consultancy and related activities": [
                        "620 - Computer programming, consultancy and related activities"
                    ],
                    "63 - Information service activities": [
                        "630 - Information service activities"
                    ],
                    "64 - Financial service activities (excluding insurance and pension funding)": [
                        "640 - Financial service activities (excluding insurance and pension funding)"
                    ],
                    "65 - Insurance, reinsurance and pension funding (excluding compulsory social security)": [
                        "650 - Insurance, reinsurance and pension funding (excluding compulsory social security)"
                    ],
                    "66 - Auxiliary activities for financial services and insurance": [
                        "660 - Auxiliary activities for financial services and insurance"
                    ],
                    "68 - Real estate activities": [
                        "680 - Real estate activities"
                    ],
                    "69 - Legal and accounting activities": [
                        "690 - Legal and accounting activities"
                    ],
                    "70 - Activities of head offices; management consultancy": [
                        "700 - Activities of head offices; management consultancy"
                    ],
                    "71 - Architectural and engineering; technical testing and analysis": [
                        "710 - Architectural and engineering; technical testing and analysis"
                    ],
                    "72 - Scientific research and development": [
                        "720 - Scientific research and development"
                    ],
                    "73 - Advertising and market research": [
                        "730 - Advertising and market research"
                    ],
                    "74 - Other professional, scientific and technical activities": [
                        "740 - Other professional, scientific and technical activities"
                    ],
                    "75 - Veterinary activities": [
                        "750 - Veterinary activities"
                    ],
                    "77 - Rental and leasing activities": [
                        "770 - Rental and leasing activities"
                    ],
                    "78 - Employment activities": [
                        "780 - Employment activities"
                    ],
                    "79 - Travel agency, tour operator, and related reservation services": [
                        "790 - Travel agency, tour operator, and related reservation services"
                    ],
                    "80 - Security and investigation activities": [
                        "800 - Security and investigation activities"
                    ],
                    "81 - Services to buildings and landscape activities": [
                        "810 - Services to buildings and landscape activities"
                    ],
                    "82 - Office administrative, support, and other business support activities": [
                        "820 - Office administrative, support, and other business support activities"
                    ],
                    "84 - Public administration and defense; compulsory social security": [
                        "840 - Public administration and defense; compulsory social security"
                    ],
                    "85 - Education": [
                        "850 - Education"
                    ],
                    "86 - Human health activities": [
                        "860 - Human health activities"
                    ],
                    "87 - Residential care activities": [
                        "870 - Residential care activities"
                    ],
                    "88 - Social work activities without accommodation": [
                        "880 - Social work activities without accommodation"
                    ],
                    "90 - Creative, arts and entertainment activities": [
                        "900 - Creative, arts and entertainment activities"
                    ],
                    "91 - Libraries, archives, museums ,and other cultural activities": [
                        "910 - Libraries, archives, museums ,and other cultural activities"
                    ],
                    "92 - Gambling and betting activities": [
                        "920 - Gambling and betting activities"
                    ],
                    "93 - Sports activities and amusement,t and recreation activities": [
                        "930 - Sports activities and amusement,t and recreation activities"
                    ],
                    "94 - Activities of membership organizations": [
                        "940 - Activities of membership organizations"
                    ],
                    "95 - Repair of computers, personal and household goods": [
                        "950 - Repair of computers, personal and household goods"
                    ],
                    "96 - Other personal service activities": [
                        "960 - Other personal service activities"
                    ],
                    "97 - Activities of households as employers of domestic personnel": [
                        "970 - Activities of households as employers of domestic personnel"
                    ],
                    "98 - Undifferentiated goods‑ and services‑producing activities of private households for own use": [
                        "980 - Undifferentiated goods‑ and services‑producing activities of private households for own use"
                    ]
                }
                # Major Activity
                major_key = f"bp_major_{form_state_key}"
                major_options = [
                    "Manufacturing/Producing", "Retailing/Trading", "Wholesaling/Trading", "Service", "Exporting", "Importing"
                ]
                if major_key not in st.session_state:
                    st.session_state[major_key] = major_options[0]
                selected_major = st.selectbox("Major Activity", major_options, key=major_key)

                # PSIC Section
                section_key = f"bp_section_{form_state_key}"
                section_options = psic_section_map.get(selected_major, ["Others"])
                if section_key not in st.session_state or st.session_state[section_key] not in section_options:
                    st.session_state[section_key] = section_options[0]
                selected_section = st.selectbox("PSIC Section", section_options, key=section_key)

                # PSIC Division
                division_key = f"bp_division_{form_state_key}"
                division_options = psic_division_map.get(selected_section, ["Others"])
                if division_key not in st.session_state or st.session_state[division_key] not in division_options:
                    st.session_state[division_key] = division_options[0]
                selected_division = st.selectbox("PSIC Division", division_options, key=division_key)

                # PSIC Group
                group_key = f"bp_group_{form_state_key}"
                group_options = psic_group_map.get(selected_division, ["Others"])
                if group_key not in st.session_state or st.session_state[group_key] not in group_options:
                    st.session_state[group_key] = group_options[0]
                selected_group = st.selectbox("PSIC Group", group_options, key=group_key)
                # Initialize session state for success message
                if 'bp_show_success' not in st.session_state:
                    st.session_state.bp_show_success = False
                    st.session_state.bp_success_timer = 0
                
                # Simple input fields without forms
                st.markdown(f"### Add Entry to {selected}")
                new_entry = {}
                
                # Major Activity/PSIC Section/Division/Group from above
                new_entry["Major Activity"] = selected_major
                new_entry["PSIC Section"] = selected_section
                new_entry["PSIC Division"] = selected_division
                new_entry["PSIC Group"] = selected_group
                
                # Row 1: Minor Activity (auto-set to Major Activity, disabled)
                st.text_input("Minor Activity", value=selected_major, disabled=True, key=f"bp_minor_{st.session_state.get('bp_form_counter', 0)}")
                new_entry["Minor Activity"] = selected_major
                
                # Row 2: Year Established and Form of Organization
                col1, col2 = st.columns(2)
                with col1:
                    new_entry["Year Established"] = st.text_input("Year Established", key=f"bp_year_{st.session_state.get('bp_form_counter', 0)}")
                with col2:
                    org_options = [
                        "Cooperative", "Corporation", "Franchise", "One Person Corporation", "Partnership", "Sole Proprietorship", "Worker's/Rural's Association"
                    ]
                    new_entry["Form of Organization"] = st.selectbox("Form of Organization", org_options, key=f"bp_org_{st.session_state.get('bp_form_counter', 0)}")
                
                # Row 3: Prio Industry Cluster
                new_entry["Prio Industry Cluster"] = st.text_input("Prio Industry Cluster", key=f"bp_cluster_{st.session_state.get('bp_form_counter', 0)}")
                
                # Submit button
                submitted = st.button("Submit")
                
                if submitted:
                    # Auto-increment 'No' and ensure order
                    data = st.session_state[table_key]
                    next_no = len(data) + 1
                    row = [str(next_no)]
                    for col in columns[1:]:
                        row.append(new_entry.get(col, ""))
                    df.loc[len(df)] = row
                    # Sort by 'No' just in case
                    df["No"] = df["No"].astype(int)
                    df = df.sort_values("No").reset_index(drop=True)
                    df["No"] = df.index + 1
                    st.session_state[table_key] = df.values.tolist()
                    save_current_data(selected)
                    
                    # Set success message flag
                    st.session_state.bp_show_success = True
                    # Clear form fields by incrementing counter
                    if 'bp_form_counter' not in st.session_state:
                        st.session_state.bp_form_counter = 0
                    st.session_state.bp_form_counter += 1
                    st.rerun()
                
                # Show success message if flag is set
                if st.session_state.bp_show_success:
                    st.success("Input saved, thank you!")
                    # Auto-hide after 3 seconds using a counter
                    if 'bp_success_timer' not in st.session_state:
                        st.session_state.bp_success_timer = 0
                    st.session_state.bp_success_timer += 1
                    if st.session_state.bp_success_timer >= 30:  # ~3 seconds
                        st.session_state.bp_show_success = False
                        st.session_state.bp_success_timer = 0
            elif selected == "Client":
                # Initialize session state for success message
                if 'client_show_success' not in st.session_state:
                    st.session_state.client_show_success = False
                    st.session_state.client_success_timer = 0
                
                # Simple input fields without forms
                st.markdown(f"### Add Entry to {selected}")
                new_entry = {}
                
                # Row 1: Date Created and Status of Client
                col1, col2 = st.columns(2)
                with col1:
                    date_created = st.date_input("Date Created", key=f"client_date_{st.session_state.get('client_form_counter', 0)}")
                    new_entry["Date Created (MM/DD/YYYY)"] = date_created.strftime("%m/%d/%Y")
                with col2:
                    new_entry["Status of Client"] = st.selectbox(
                        "Status of Client",
                        [
                            "Level 0 - Would be or Potential Entrepreneurs",
                            "Level 1 - Nurturing Startup",
                            "Level 2 - Growing Enterprises (Registered)",
                            "Level 3 - Expanding Enterprises (Registered)",
                            "Level 4 - Sustaining Enterprises"
                        ],
                        key=f"client_status_{st.session_state.get('client_form_counter', 0)}"
                    )
                
                # Row 2: Category and Social Classification
                col1, col2 = st.columns(2)
                with col1:
                    new_entry["Category of Client"] = st.selectbox(
                        "Category of Client",
                        ["Retiree", "Self-Employed", "Senior Citizen", "Student", "Unemployed", "Urban Poor", "Youth"],
                        key=f"client_category_{st.session_state.get('client_form_counter', 0)}"
                    )
                with col2:
                    new_entry["Social Classification"] = st.selectbox(
                        "Social Classification",
                        ["Abled", "Person with Disabilities"],
                        key=f"client_social_{st.session_state.get('client_form_counter', 0)}"
                    )
                
                # Row 3: Senior and Indigenous
                col1, col2 = st.columns(2)
                with col1:
                    new_entry["Client is Senior"] = st.selectbox(
                        "Client is Senior",
                        ["Yes", "No"],
                        key=f"client_senior_{st.session_state.get('client_form_counter', 0)}"
                    )
                with col2:
                    new_entry["Client is Indigenous"] = st.selectbox(
                        "Client is Indigenous",
                        ["Yes", "No"],
                        key=f"client_indigenous_{st.session_state.get('client_form_counter', 0)}"
                    )
                
                # Row 4: Level of Digitalization (full width)
                new_entry["Level of Digitalization"] = st.selectbox(
                    "Level of Digitalization",
                    [
                        "Level 0 - No use of digital tools",
                        "Level 1 (Basic) - MSMEs that use basic digital tools for business",
                        "Level 2 (Intermediate) - MSMEs that have an online presence",
                        "Level 3 (Advanced) - Use of advanced digital tools"
                    ],
                    key=f"client_digital_{st.session_state.get('client_form_counter', 0)}"
                )
                
                # Row 5: Client Designation
                new_entry["Client Designation"] = st.selectbox(
                    "Client Designation",
                    ["Owner", "Representative"],
                    key=f"client_designation_{st.session_state.get('client_form_counter', 0)}"
                )
                
                # Row 6: Name fields
                col1, col2 = st.columns(2)
                with col1:
                    new_entry["First Name"] = st.text_input("First Name", key=f"client_first_name_{st.session_state.get('client_form_counter', 0)}")
                with col2:
                    new_entry["Last Name"] = st.text_input("Last Name", key=f"client_last_name_{st.session_state.get('client_form_counter', 0)}")
                
                # Row 7: Civil Status and Sex
                col1, col2 = st.columns(2)
                with col1:
                    new_entry["Civil Status"] = st.text_input("Civil Status", key=f"client_civil_status_{st.session_state.get('client_form_counter', 0)}")
                with col2:
                    new_entry["Sex"] = st.text_input("Sex", key=f"client_sex_{st.session_state.get('client_form_counter', 0)}")
                
                # Row 8: Barangay and District
                col1, col2 = st.columns(2)
                with col1:
                    new_entry["Barangay"] = st.text_input("Barangay", key=f"client_barangay_{st.session_state.get('client_form_counter', 0)}")
                with col2:
                    new_entry["District"] = st.text_input("District", key=f"client_district_{st.session_state.get('client_form_counter', 0)}")
                
                # Row 9: Address (full width)
                new_entry["Address"] = st.text_input("Address", key=f"client_address_{st.session_state.get('client_form_counter', 0)}")
                
                # Row 10: Mobile Number and Email Address
                col1, col2 = st.columns(2)
                with col1:
                    new_entry["Mobile Number"] = st.text_input("Mobile Number", key=f"client_mobile_number_{st.session_state.get('client_form_counter', 0)}")
                with col2:
                    new_entry["Email Address"] = st.text_input("Email Address", key=f"client_email_address_{st.session_state.get('client_form_counter', 0)}")
                
                # Submit button
                submitted = st.button("Submit")
                
                if submitted:
                    # Auto-increment 'No' and ensure order
                    data = st.session_state[table_key]
                    next_no = len(data) + 1
                    row = [str(next_no)]
                    for col in columns[1:]:
                        row.append(new_entry.get(col, ""))
                    df.loc[len(df)] = row
                    # Sort by 'No' just in case
                    df["No"] = df["No"].astype(int)
                    df = df.sort_values("No").reset_index(drop=True)
                    df["No"] = df.index + 1
                    st.session_state[table_key] = df.values.tolist()
                    save_current_data(selected)
                    
                    # Set success message flag
                    st.session_state.client_show_success = True
                    # Clear form fields by incrementing counter
                    if 'client_form_counter' not in st.session_state:
                        st.session_state.client_form_counter = 0
                    st.session_state.client_form_counter += 1
                    st.rerun()
                
                # Show success message if flag is set
                if st.session_state.client_show_success:
                    st.success("Input saved, thank you!")
                    # Auto-hide after 3 seconds using a counter
                    if 'client_success_timer' not in st.session_state:
                        st.session_state.client_success_timer = 0
                    st.session_state.client_success_timer += 1
                    if st.session_state.client_success_timer >= 30:  # ~3 seconds
                        st.session_state.client_show_success = False
                        st.session_state.client_success_timer = 0
            elif selected == "Business Financial Structure":
                # Initialize session state for success message
                if 'bfs_show_success' not in st.session_state:
                    st.session_state.bfs_show_success = False
                    st.session_state.bfs_success_timer = 0
                
                # Simple input fields without forms
                st.markdown(f"### Add Entry to {selected}")
                new_entry = {}
                for col in columns[1:]:  # Skip 'No'
                    new_entry[col] = st.text_input(col, key=f"bfs_{col.replace(' ', '_').lower()}_{st.session_state.get('bfs_form_counter', 0)}")
                
                # Submit button
                submitted = st.button("Submit")
                
                if submitted:
                    # Auto-increment 'No' and ensure order
                    data = st.session_state[table_key]
                    next_no = len(data) + 1
                    row = [str(next_no)]
                    for col in columns[1:]:
                        row.append(new_entry.get(col, ""))
                    df.loc[len(df)] = row
                    # Sort by 'No' just in case
                    df["No"] = df["No"].astype(int)
                    df = df.sort_values("No").reset_index(drop=True)
                    df["No"] = df.index + 1
                    st.session_state[table_key] = df.values.tolist()
                    save_current_data(selected)
                    
                    # Set success message flag
                    st.session_state.bfs_show_success = True
                    # Clear form fields by incrementing counter
                    if 'bfs_form_counter' not in st.session_state:
                        st.session_state.bfs_form_counter = 0
                    st.session_state.bfs_form_counter += 1
                    st.rerun()
                
                # Show success message if flag is set
                if st.session_state.bfs_show_success:
                    st.success("Input saved, thank you!")
                    # Auto-hide after 3 seconds using a counter
                    if 'bfs_success_timer' not in st.session_state:
                        st.session_state.bfs_success_timer = 0
                    st.session_state.bfs_success_timer += 1
                    if st.session_state.bfs_success_timer >= 30:  # ~3 seconds
                        st.session_state.bfs_show_success = False
                        st.session_state.bfs_success_timer = 0
            elif selected == "Market Domestic":
                # Simple input fields without forms
                st.markdown(f"### Add Entry to {selected}")
                new_entry = {}
                
                # Product/Service
                new_entry["Product/Service"] = st.text_input("Product/Service", key=f"md_product_{st.session_state.get('md_form_counter', 0)}")
                
                # Location Information
                st.markdown("#### Location Information")
                location_data = create_location_widgets()
                new_entry["Region"] = location_data["region"]
                new_entry["Province"] = location_data["province"]
                new_entry["City/Municipality"] = location_data["city"]
                new_entry["Barangay"] = location_data["barangay"]
                new_entry["Purok"] = location_data["purok"]
                
                # Address Information
                st.markdown("#### Address Information")
                new_entry["District"] = st.text_input("District", key=f"md_district_{st.session_state.get('md_form_counter', 0)}")
                new_entry["Address"] = st.text_input("Address", key=f"md_address_{st.session_state.get('md_form_counter', 0)}")
                new_entry["Zip Code"] = st.text_input("Zip Code", key=f"md_zip_code_{st.session_state.get('md_form_counter', 0)}")
                
                # Submit button
                submitted = st.button("Submit")
                
                if submitted:
                    # Auto-increment 'No' and ensure order
                    data = st.session_state[table_key]
                    next_no = len(data) + 1
                    row = [str(next_no)]
                    for col in columns[1:]:
                        if col == "Product/Service":
                            row.append(new_entry.get("Product/Service", ""))
                        elif col == "Region":
                            row.append(new_entry.get("Region", ""))
                        elif col == "Province":
                            row.append(new_entry.get("Province", ""))
                        else:
                            row.append("")
                    df.loc[len(df)] = row
                    # Sort by 'No' just in case
                    df["No"] = df["No"].astype(int)
                    df = df.sort_values("No").reset_index(drop=True)
                    df["No"] = df.index + 1
                    st.session_state[table_key] = df.values.tolist()
                    
                    # Set success message flag
                    st.session_state.md_show_success = True
                    # Increment counter to clear text inputs
                    st.session_state.md_form_counter = st.session_state.get('md_form_counter', 0) + 1
                    # Clear location dropdowns
                    st.session_state.loc_region = None
                    st.session_state.loc_province = None
                    st.session_state.loc_city = None
                    st.session_state.loc_barangay = None
                    st.rerun()
                
                # Show success message if flag is set
                if st.session_state.get('md_show_success', False):
                    st.success("Input saved, thank you!")
                    # Auto-hide after 3 seconds using a counter
                    if 'md_success_timer' not in st.session_state:
                        st.session_state.md_success_timer = 0
                    st.session_state.md_success_timer += 1
                    if st.session_state.md_success_timer >= 30:  # ~3 seconds
                        st.session_state.md_show_success = False
                        st.session_state.md_success_timer = 0
            elif selected == "Market Export":
                # Year Export Started dropdown (2030-2010)
                year_options = [str(y) for y in range(2030, 2009, -1)]
                # Country dropdown (alphabetical)
                country_options = [
                    'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Australia', 'Austria', 'Azerbaijan',
                    'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan', 'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi',
                    'Cabo Verde', 'Cambodia', 'Cameroon', 'Canada', 'Central African Republic', 'Chad', 'Chile', 'China', 'Colombia', 'Comoros', 'Congo', 'Costa Rica', 'Croatia', 'Cuba', 'Cyprus', 'Czech Republic',
                    'Democratic Republic of the Congo', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic',
                    'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Eswatini', 'Ethiopia',
                    'Fiji', 'Finland', 'France',
                    'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Grenada', 'Guatemala', 'Guinea', 'Guinea-Bissau', 'Guyana',
                    'Haiti', 'Honduras', 'Hungary',
                    'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel', 'Italy',
                    'Jamaica', 'Japan', 'Jordan',
                    'Kazakhstan', 'Kenya', 'Kiribati', 'Kuwait', 'Kyrgyzstan',
                    'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg',
                    'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania', 'Mauritius', 'Mexico', 'Micronesia', 'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar',
                    'Namibia', 'Nauruan', 'Nepal', 'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'North Korea', 'North Macedonia', 'Norway',
                    'Oman',
                    'Pakistan', 'Palau', 'Palestine', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal',
                    'Qatar',
                    'Romania', 'Russia', 'Rwanda',
                    'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Samoa', 'San Marino', 'Sao Tome and Principe', 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 'South Korea', 'South Sudan', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Sweden', 'Switzerland', 'Syria',
                    'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Timor-Leste', 'Togo', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Tuvalu',
                    'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States', 'Uruguay', 'Uzbekistan',
                    'Vanuatu', 'Vatican City', 'Venezuela', 'Vietnam',
                    'Yemen',
                    'Zambia', 'Zimbabwe'
                ]
                country_options = sorted(country_options)
                # Initialize session state for success message
                if 'me_show_success' not in st.session_state:
                    st.session_state.me_show_success = False
                    st.session_state.me_success_timer = 0
                
                # Simple input fields without forms
                st.markdown(f"### Add Entry to {selected}")
                new_entry = {}
                
                # Row 1: Year Export Started and Country
                col1, col2 = st.columns(2)
                with col1:
                    new_entry["Year Export Started"] = st.selectbox("Year Export Started", year_options, key=f"me_year_{st.session_state.get('me_form_counter', 0)}")
                with col2:
                    new_entry["Country"] = st.selectbox("Country", country_options, key=f"me_country_{st.session_state.get('me_form_counter', 0)}")
                
                # Row 2: Product Service and Trade Bloc
                col1, col2 = st.columns(2)
                with col1:
                    new_entry["Product Service"] = st.text_input("Product Service", key=f"me_product_{st.session_state.get('me_form_counter', 0)}")
                with col2:
                    new_entry["Trade Bloc"] = st.text_input("Trade Bloc", key=f"me_trade_bloc_{st.session_state.get('me_form_counter', 0)}")
                
                # Submit button
                submitted = st.button("Submit")
                
                if submitted:
                    # Auto-increment 'No' and ensure order
                    data = st.session_state[table_key]
                    next_no = len(data) + 1
                    row = [str(next_no)]
                    for col in columns[1:]:
                        row.append(new_entry.get(col, ""))
                    df.loc[len(df)] = row
                    # Sort by 'No' just in case
                    df["No"] = df["No"].astype(int)
                    df = df.sort_values("No").reset_index(drop=True)
                    df["No"] = df.index + 1
                    st.session_state[table_key] = df.values.tolist()
                    save_current_data(selected)
                    
                    # Set success message flag
                    st.session_state.me_show_success = True
                    # Clear form fields by incrementing counter
                    if 'me_form_counter' not in st.session_state:
                        st.session_state.me_form_counter = 0
                    st.session_state.me_form_counter += 1
                    st.rerun()
                
                # Show success message if flag is set
                if st.session_state.me_show_success:
                    st.success("Input saved, thank you!")
                    # Auto-hide after 3 seconds using a counter
                    if 'me_success_timer' not in st.session_state:
                        st.session_state.me_success_timer = 0
                    st.session_state.me_success_timer += 1
                    if st.session_state.me_success_timer >= 30:  # ~3 seconds
                        st.session_state.me_show_success = False
                        st.session_state.me_success_timer = 0
            elif selected == "Market Import":
                # Year Import Started dropdown (2030-2010)
                year_options = [str(y) for y in range(2030, 2010-1, -1)]
                # Country dropdown (alphabetical)
                country_options = [
                    'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Australia', 'Austria', 'Azerbaijan',
                    'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan', 'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi',
                    'Cabo Verde', 'Cambodia', 'Cameroon', 'Canada', 'Central African Republic', 'Chad', 'Chile', 'China', 'Colombia', 'Comoros', 'Congo', 'Costa Rica', 'Croatia', 'Cuba', 'Cyprus', 'Czech Republic',
                    'Democratic Republic of the Congo', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic',
                    'Ecuador', 'Egypt', 'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Eswatini', 'Ethiopia',
                    'Fiji', 'Finland', 'France',
                    'Gabon', 'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Grenada', 'Guatemala', 'Guinea', 'Guinea-Bissau', 'Guyana',
                    'Haiti', 'Honduras', 'Hungary',
                    'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel', 'Italy',
                    'Jamaica', 'Japan', 'Jordan',
                    'Kazakhstan', 'Kenya', 'Kiribati', 'Kuwait', 'Kyrgyzstan',
                    'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg',
                    'Madagascar', 'Malawi', 'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania', 'Mauritius', 'Mexico', 'Micronesia', 'Moldova', 'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar',
                    'Namibia', 'Nauruan', 'Nepal', 'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'North Korea', 'North Macedonia', 'Norway',
                    'Oman',
                    'Pakistan', 'Palau', 'Palestine', 'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal',
                    'Qatar',
                    'Romania', 'Russia', 'Rwanda',
                    'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Samoa', 'San Marino', 'Sao Tome and Principe', 'Saudi Arabia', 'Senegal', 'Serbia', 'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 'South Korea', 'South Sudan', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Sweden', 'Switzerland', 'Syria',
                    'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Timor-Leste', 'Togo', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Tuvalu',
                    'Uganda', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States', 'Uruguay', 'Uzbekistan',
                    'Vanuatu', 'Vatican City', 'Venezuela', 'Vietnam',
                    'Yemen',
                    'Zambia', 'Zimbabwe'
                ]
                country_options = sorted(country_options)
                # Initialize session state for success message
                if 'mi_show_success' not in st.session_state:
                    st.session_state.mi_show_success = False
                    st.session_state.mi_success_timer = 0
                
                # Simple input fields without forms
                st.markdown(f"### Add Entry to {selected}")
                new_entry = {}
                
                # Row 1: Year Import Started and Country
                col1, col2 = st.columns(2)
                with col1:
                    new_entry["Year Import Started"] = st.selectbox("Year Import Started", year_options, key=f"mi_year_{st.session_state.get('mi_form_counter', 0)}")
                with col2:
                    new_entry["Country"] = st.selectbox("Country", country_options, key=f"mi_country_{st.session_state.get('mi_form_counter', 0)}")
                
                # Row 2: Product Service
                new_entry["Product Service"] = st.text_input("Product Service", key=f"mi_product_{st.session_state.get('mi_form_counter', 0)}")
                
                # Submit button
                submitted = st.button("Submit")
                
                if submitted:
                    # Auto-increment 'No' and ensure order
                    data = st.session_state[table_key]
                    next_no = len(data) + 1
                    row = [str(next_no)]
                    for col in columns[1:]:
                        row.append(new_entry.get(col, ""))
                    df.loc[len(df)] = row
                    # Sort by 'No' just in case
                    df["No"] = df["No"].astype(int)
                    df = df.sort_values("No").reset_index(drop=True)
                    df["No"] = df.index + 1
                    st.session_state[table_key] = df.values.tolist()
                    save_current_data(selected)
                    
                    # Set success message flag
                    st.session_state.mi_show_success = True
                    # Clear form fields by incrementing counter
                    if 'mi_form_counter' not in st.session_state:
                        st.session_state.mi_form_counter = 0
                    st.session_state.mi_form_counter += 1
                    st.rerun()
                
                # Show success message if flag is set
                if st.session_state.mi_show_success:
                    st.success("Input saved, thank you!")
                    # Auto-hide after 3 seconds using a counter
                    if 'mi_success_timer' not in st.session_state:
                        st.session_state.mi_success_timer = 0
                    st.session_state.mi_success_timer += 1
                    if st.session_state.mi_success_timer >= 30:  # ~3 seconds
                        st.session_state.mi_show_success = False
                        st.session_state.mi_success_timer = 0
            elif selected == "Product_Service Lines":
                # Initialize session state for success message
                if 'psl_show_success' not in st.session_state:
                    st.session_state.psl_show_success = False
                    st.session_state.psl_success_timer = 0
                
                # Simple input fields without forms
                st.markdown(f"### Add Entry to {selected}")
                new_entry = {}
                
                # Row 1: Product/Service Line and Major Raw Material/s
                col1, col2 = st.columns(2)
                with col1:
                    new_entry["Product/Service Line"] = st.text_input("Product/Service Line", key=f"psl_product_{st.session_state.get('psl_form_counter', 0)}")
                with col2:
                    new_entry["Major Raw Material/s"] = st.text_input("Major Raw Material/s", key=f"psl_material_{st.session_state.get('psl_form_counter', 0)}")
                
                # Submit button
                submitted = st.button("Submit")
                
                if submitted:
                    # Auto-increment 'No' and ensure order
                    data = st.session_state[table_key]
                    next_no = len(data) + 1
                    row = [str(next_no)]
                    for col in columns[1:]:
                        row.append(new_entry.get(col, ""))
                    df.loc[len(df)] = row
                    # Sort by 'No' just in case
                    df["No"] = df["No"].astype(int)
                    df = df.sort_values("No").reset_index(drop=True)
                    df["No"] = df.index + 1
                    st.session_state[table_key] = df.values.tolist()
                    save_current_data(selected)
                    
                    # Set success message flag
                    st.session_state.psl_show_success = True
                    # Clear form fields by incrementing counter
                    if 'psl_form_counter' not in st.session_state:
                        st.session_state.psl_form_counter = 0
                    st.session_state.psl_form_counter += 1
                    st.rerun()
                
                # Show success message if flag is set
                if st.session_state.psl_show_success:
                    st.success("Input saved, thank you!")
                    # Auto-hide after 3 seconds using a counter
                    if 'psl_success_timer' not in st.session_state:
                        st.session_state.psl_success_timer = 0
                    st.session_state.psl_success_timer += 1
                    if st.session_state.psl_success_timer >= 30:  # ~3 seconds
                        st.session_state.psl_show_success = False
                        st.session_state.psl_success_timer = 0
            elif selected == "Assistance":
                # EDT Assistance Level options
                edt_levels = [
                    "Level 0 - Entrepreneurial Mind Setting",
                    "Level 1.1 - Nurturing Startup (Not Registered)",
                    "Level 1.2 - Nurturing Start Up (Partially Registered)",
                    "Level 2 - Growing Enterprises",
                    "Level 3 - Expanding Enterprises",
                    "Level 4 - Sustaining Enterprises"
                ]
                
                # Type of Assistance options
                assistance_types = [
                    "Business Registration/Facilitation",
                    "Consumer Related Assistance",
                    "Ecommerce/MSME Digitalization",
                    "Investment Promotion",
                    "Product Development",
                    "Production",
                    "Training and Seminar"
                ]
                
                # Sub Type of Assistance mapping by Type of Assistance
                sub_type_map = {
                    "Business Registration/Facilitation": [
                        "Business Registration", "SEC Registration", "CDA Registration", "DOLE Registration",
                        "BMBE Registration", "LGU/Mayor's Permit", "FDA Registration", "Other Permits"
                    ],
                    "Consumer Related Assistance": [
                        "Accreditation Facilitation", "Application for DTI - Certified Establishment (DTI - Bagwis Program)",
                        "Accreditation of Service and Repair Shop", "Application for Sales Promotion Permit",
                        "Accreditation of Truck Rebuilding Center", "Accreditation of Private Emission Testing Center",
                        "Product Standards Conformance", "Complaint Handling"
                    ],
                    "Ecommerce/MSME Digitalization": [
                        "Webinar", "Social Media Platform Creation", "Ecommerce Enrollment",
                        "Website Design", "Geo Tagging (e.g., Google Map)", "Others"
                    ],
                    "Investment Promotion": [
                        "Investment Promotion-Related Services Rendered", "Investment Mission",
                        "Investment Exhibit", "Business Matching", "Investment Briefing", "Investment Forum/Conference"
                    ],
                    "Product Development": [
                        "Product Clinic Facilitated", "Product Catalogue/Profiles",
                        "Packaging Designs Developed/Improved", "Labelling Designs Developed/Improved",
                        "Prototypes Developed", "Other ProDev Related Services Rendered"
                    ],
                    "Production": [
                        "Technology Facilitation", "Business Incubation Services", "Raw Materials Procurement",
                        "SSF Machinery and Equipment", "Production Process", "Plant Lay-out Consultancy"
                    ],
                    "Training and Seminar": [
                        "Business Opportunities", "Entrepreneurship Seminars", "Managerial/Technical", "Skills Training"
                    ]
                }
                
                # MSME Program options
                msme_programs = [
                    "Negosyo Center", "One Town, One Product (OTOP)", "Pangkabuhayan para sa Pagbangon at Ginhawa (PPG)",
                    "Pondo sa Pagbabago at Pag-asenso (P3) / Other Financing Services through SB CORP",
                    "Regional Interactive Platform for Philippine Exporters (RIPPLES)",
                    "Rural Agro-Enterprise Partnership for Inclusive Development (RAPID) Growth Project",
                    "Shared Service Facilities (SSF)", "SME Roving Academy (SMERA)"
                ]
                
                # Assisting Office options
                assisting_offices = [
                    "Technical Admin (ISMS)", "Negosyo Center", "Provincial Office Admin",
                    "Project Management Office", "Regional Office Admin", "Head Office"
                ]
                
                # Assisting Officer Region options
                officer_regions = [
                    "National Capital Region (NCR)", "Cordillera Administrative Region (CAR)",
                    "Region 1 (Ilocos Region)", "Region 2 (Cagayan Valley)", "Region 3 (Central Luzon)",
                    "Region 4-A CALABARZON", "MIMAROPA", "Region 5 (Bicol Region)",
                    "Region 6 (Western Visayas)", "Region 7 (Central Visayas)", "Region 8 (Eastern Visayas)",
                    "Region 9 (Zamboanga Peninsula)", "Region 10 (Northern Mindanao)", "Region 11 (Davao Region)",
                    "Region 12 (SOCCSKSARGEN)", "Region 13 CARAGA", "BARMM"
                ]
                
                # Step 1: Select Type of Assistance and Sub Type (outside form for dynamic updates)
                st.markdown("#### Step 1: Select Type of Assistance and Sub Type")
                selected_assistance_type = st.selectbox("Type of Assistance", assistance_types)
                sub_type_options = sub_type_map.get(selected_assistance_type, [])
                selected_sub_type = st.selectbox("Sub Type of Assistance", sub_type_options)
                
                # Step 2: Select Assisting Officer Location
                st.markdown("#### Step 2: Select Assisting Officer Location")
                st.markdown("**Assisting Officer Location Information**")
                officer_location_data = create_location_widgets()
                
                # Initialize session state for success message
                if 'assistance_show_success' not in st.session_state:
                    st.session_state.assistance_show_success = False
                    st.session_state.assistance_success_timer = 0
                
                # Simple input fields without forms
                st.markdown(f"### Add Entry to {selected}")
                new_entry = {}
                
                # Type of Assistance and Sub Type (from outside form)
                new_entry["Type of Assistance"] = selected_assistance_type
                new_entry["Sub Type of Asisstance"] = selected_sub_type
                
                # Assisting Officer Location (from outside form)
                new_entry["Assisting Officer Region"] = officer_location_data["region"]
                new_entry["Assisting Officer Province"] = officer_location_data["province"]
                new_entry["Assisting Officer City"] = officer_location_data["city"]
                new_entry["Assisting Officer Barangay"] = officer_location_data["barangay"]
                new_entry["Assisting Officer Purok"] = officer_location_data["purok"]
                
                # Row 1: EDT Assistance Level and MSME Program
                col1, col2 = st.columns(2)
                with col1:
                    new_entry["EDT Assistance Level"] = st.selectbox("EDT Assistance Level", edt_levels, key=f"assistance_edt_{st.session_state.get('assistance_form_counter', 0)}")
                with col2:
                    new_entry["MSME Program"] = st.selectbox("MSME Program", msme_programs, key=f"assistance_msme_{st.session_state.get('assistance_form_counter', 0)}")
                
                # Row 2: Date Start and Date End
                col1, col2 = st.columns(2)
                with col1:
                    date_start = st.date_input("Date Start", key=f"assistance_start_{st.session_state.get('assistance_form_counter', 0)}")
                    new_entry["Date Start (MM/DD/YYYY)"] = date_start.strftime("%m/%d/%Y")
                with col2:
                    date_end = st.date_input("Date End", key=f"assistance_end_{st.session_state.get('assistance_form_counter', 0)}")
                    new_entry["Date End (MM/DD/YYYY)"] = date_end.strftime("%m/%d/%Y")
                
                # Row 3: MSME Availed and Assisting Office
                col1, col2 = st.columns(2)
                with col1:
                    msme_availed_date = st.date_input("MSME Availed", key=f"assistance_availed_{st.session_state.get('assistance_form_counter', 0)}")
                    new_entry["MSME Availed (MM/DD/YYYY)"] = msme_availed_date.strftime("%m/%d/%Y")
                with col2:
                    new_entry["Assisting Office"] = st.selectbox("Assisting Office", assisting_offices, key=f"assistance_office_{st.session_state.get('assistance_form_counter', 0)}")
                
                # Row 4: Remarks and Assisted By
                col1, col2 = st.columns(2)
                with col1:
                    new_entry["Remarks"] = st.text_input("Remarks", key=f"assistance_remarks_{st.session_state.get('assistance_form_counter', 0)}")
                with col2:
                    new_entry["Assisted By"] = st.text_input("Assisted By", key=f"assistance_by_{st.session_state.get('assistance_form_counter', 0)}")
                
                # Submit button
                submitted = st.button("Submit")
                
                if submitted:
                    # Auto-increment 'No' and ensure order
                    data = st.session_state[table_key]
                    next_no = len(data) + 1
                    row = [str(next_no)]
                    for col in columns[1:]:
                        row.append(new_entry.get(col, ""))
                    df.loc[len(df)] = row
                    # Sort by 'No' just in case
                    df["No"] = df["No"].astype(int)
                    df = df.sort_values("No").reset_index(drop=True)
                    df["No"] = df.index + 1
                    st.session_state[table_key] = df.values.tolist()
                    save_current_data(selected)
                    
                    # Set success message flag
                    st.session_state.assistance_show_success = True
                    # Clear form fields by incrementing counter
                    if 'assistance_form_counter' not in st.session_state:
                        st.session_state.assistance_form_counter = 0
                    st.session_state.assistance_form_counter += 1
                    st.rerun()
                
                # Show success message if flag is set
                if st.session_state.assistance_show_success:
                    st.success("Input saved, thank you!")
                    # Auto-hide after 3 seconds using a counter
                    if 'assistance_success_timer' not in st.session_state:
                        st.session_state.assistance_success_timer = 0
                    st.session_state.assistance_success_timer += 1
                    if st.session_state.assistance_success_timer >= 30:  # ~3 seconds
                        st.session_state.assistance_show_success = False
                        st.session_state.assistance_success_timer = 0
            elif selected == "Jobs Generated":
                # Initialize session state for success message
                if 'jobs_show_success' not in st.session_state:
                    st.session_state.jobs_show_success = False
                    st.session_state.jobs_success_timer = 0
                
                # Simple input fields without forms
                st.markdown(f"### Add Entry to {selected}")
                new_entry = {}
                
                # Row 1: Date Recorded
                date_recorded = st.date_input("Date Recorded", key=f"jobs_date_{st.session_state.get('jobs_form_counter', 0)}")
                new_entry["Date Recorded (MM/DD/YYYY)"] = date_recorded.strftime("%m/%d/%Y")
                
                # Row 2: Direct Community Jobs and Direct Home Based
                col1, col2 = st.columns(2)
                with col1:
                    new_entry["Direct Community Jobs"] = st.text_input("Direct Community Jobs", key=f"jobs_community_{st.session_state.get('jobs_form_counter', 0)}")
                with col2:
                    new_entry["Direct Home Based"] = st.text_input("Direct Home Based", key=f"jobs_home_{st.session_state.get('jobs_form_counter', 0)}")
                
                # Row 3: Indirect Home Based and Direct Jobs Sustained
                col1, col2 = st.columns(2)
                with col1:
                    new_entry["Indirect Home Based"] = st.text_input("Indirect Home Based", key=f"jobs_indirect_{st.session_state.get('jobs_form_counter', 0)}")
                with col2:
                    new_entry["Direct Jobs Sustained"] = st.text_input("Direct Jobs Sustained", key=f"jobs_sustained_{st.session_state.get('jobs_form_counter', 0)}")
                
                # Submit button
                submitted = st.button("Submit")
                
                if submitted:
                    # Auto-increment 'No' and ensure order
                    data = st.session_state[table_key]
                    next_no = len(data) + 1
                    row = [str(next_no)]
                    for col in columns[1:]:
                        row.append(new_entry.get(col, ""))
                    df.loc[len(df)] = row
                    # Sort by 'No' just in case
                    df["No"] = df["No"].astype(int)
                    df = df.sort_values("No").reset_index(drop=True)
                    df["No"] = df.index + 1
                    st.session_state[table_key] = df.values.tolist()
                    save_current_data(selected)
                    
                    # Set success message flag
                    st.session_state.jobs_show_success = True
                    # Clear form fields by incrementing counter
                    if 'jobs_form_counter' not in st.session_state:
                        st.session_state.jobs_form_counter = 0
                    st.session_state.jobs_form_counter += 1
                    st.rerun()
                
                # Show success message if flag is set
                if st.session_state.jobs_show_success:
                    st.success("Input saved, thank you!")
                    # Auto-hide after 3 seconds using a counter
                    if 'jobs_success_timer' not in st.session_state:
                        st.session_state.jobs_success_timer = 0
                    st.session_state.jobs_success_timer += 1
                    if st.session_state.jobs_success_timer >= 30:  # ~3 seconds
                        st.session_state.jobs_show_success = False
                        st.session_state.jobs_success_timer = 0

        # After all form logic, always show the table for the selected sheet
        st.markdown(
            '''
    <style>
            .stDataFrameContainer, .stDataEditorContainer {
        width: 100vw !important;
        max-width: 100vw !important;
                min-width: 100vw !important;
            }
            .block-container {
                padding-left: 20 !important;
                padding-right: 20 !important;
                max-width: 100vw !important;
    }
    </style>
            ''',
    unsafe_allow_html=True,
        )
        # Create data editor with automatic saving
        edited_df = st.data_editor(
            df,
            key=f"editor_{selected}",
            num_rows="dynamic",
            use_container_width=True,
            column_config=column_config,
            hide_index=True
        )
        
        # Save data whenever it changes
        if not edited_df.equals(df):
            st.session_state[table_key] = edited_df.values.tolist()
            save_current_data(selected)
        
        # Also save data after form submissions
        if f"form_submitted_{selected}" not in st.session_state:
            st.session_state[f"form_submitted_{selected}"] = False
        
        if st.session_state[f"form_submitted_{selected}"]:
            save_current_data(selected)
            st.session_state[f"form_submitted_{selected}"] = False
        
        # Save data after any table changes (including form submissions)
        save_current_data(selected)
    
    # Close main content wrapper
    st.markdown('</div>', unsafe_allow_html=True)
