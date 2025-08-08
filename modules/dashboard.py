import streamlit as st
import numpy as np
import pandas as pd
import json
import os
from utils.philippine_locations import create_location_widgets
from utils.psic_handler import create_psic_widgets

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
        /* Force wide layout and full width utilization */
        .appview-container .main .block-container {
            max-width: 100% !important;
            width: 100% !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-top: 0.5rem !important;
        }
        
        /* Target the main content area more specifically */
        section[data-testid="stAppViewContainer"] .main .block-container {
            max-width: none !important;
            width: 100% !important;
            padding-top: 0.5rem !important;
        }
        
        /* Remove any width constraints on the main container */
        .main {
            width: 100% !important;
            max-width: none !important;
        }
        
        .main > div {
            width: 100% !important;
            max-width: none !important;
        }
        
        /* Reduce spacing around headers */
        .main h1, .main h2, .main h3 {
            margin-top: 0.5rem !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Reduce spacing around markdown elements */
        .main .markdown-text-container {
            margin-top: 0 !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Reduce spacing in the main content area */
        .main .element-container {
            margin-bottom: 0.5rem !important;
        }
        
        /* Ensure data tables use full width */
        .stDataFrame,
        .stDataEditor {
            width: 100% !important;
        }
        
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
        
        /* Force container to use full viewport width when sidebar is collapsed */
        .css-1d391kg {
            width: 100% !important;
            max-width: 100vw !important;
        }
        
        /* Override Streamlit's default container width limits */
        .css-k1vhr4, .css-18e3th9 {
            max-width: none !important;
            width: 100% !important;
        }
        
        /* Make table column headers bold and black */
        thead tr th {
            font-weight: bold !important;
            color: black !important;
        }
        
        /* Style required field asterisks in red */
        /* Target all labels and make asterisks red using CSS pseudo-elements */
        label[data-testid="stWidgetLabel"] {
            position: relative;
        }
        
        /* More aggressive approach - target any text ending with asterisk */
        label[data-testid="stWidgetLabel"]:after {
            content: "";
        }
        
        /* Direct CSS approach for red asterisks */
        .stSelectbox label, 
        .stTextInput label, 
        .stDateInput label, 
        .stNumberInput label,
        label[data-testid="stWidgetLabel"] {
            color: #333333 !important;
        }
        
        /* Use CSS to make asterisks red - more reliable method */
        .main label:has-text("*") * {
            color: inherit;
        }
        
        /* Alternative: Use important CSS selectors */
        div[data-testid="stSelectbox"] label::after,
        div[data-testid="stTextInput"] label::after,
        div[data-testid="stDateInput"] label::after {
            color: red !important;
        }
        
        /* Most reliable method: inline styling for asterisks */
        .required-asterisk {
            color: #ff0000 !important;
            font-weight: bold !important;
            font-size: 1.1em !important;
        }
        
        /* Target specific text content */
        label[data-testid="stWidgetLabel"] {
            color: #262730 !important;
        }
        
        /* Red asterisks using text replacement */
        .red-asterisk {
            color: #ff0000 !important;
            font-weight: bold !important;
        }
        </style>
        
        <script>
        // Function to make asterisks red
        function styleAsterisks() {
            // Method 1: Target Streamlit widget labels
            const labels = document.querySelectorAll('label[data-testid="stWidgetLabel"]');
            labels.forEach(label => {
                if (label.textContent.includes('*')) {
                    // Replace asterisks with red styled version
                    const originalHTML = label.innerHTML;
                    label.innerHTML = originalHTML.replace(/\*/g, '<span style="color: #ff0000 !important; font-weight: bold !important;">*</span>');
                }
            });
            
            // Method 2: Target all labels in the main content
            const allLabels = document.querySelectorAll('.main label, .stform label');
            allLabels.forEach(label => {
                if (label.textContent.includes('*')) {
                    const text = label.innerHTML;
                    label.innerHTML = text.replace(/\*/g, '<span style="color: #ff0000 !important; font-weight: bold !important;">*</span>');
                }
            });
            
            // Method 3: Target selectbox and input labels specifically
            const inputLabels = document.querySelectorAll('.stSelectbox label, .stTextInput label, .stDateInput label, .stNumberInput label');
            inputLabels.forEach(label => {
                if (label.textContent.includes('*')) {
                    const text = label.innerHTML;
                    label.innerHTML = text.replace(/\*/g, '<span style="color: #ff0000 !important; font-weight: bold !important; font-size: 1.1em !important;">*</span>');
                }
            });
            
            // Method 4: More aggressive approach - find all text nodes with asterisks
            const walker = document.createTreeWalker(
                document.querySelector('.main'),
                NodeFilter.SHOW_TEXT,
                null,
                false
            );
            
            const textNodes = [];
            let node;
            while (node = walker.nextNode()) {
                if (node.textContent.includes('*') && node.parentElement.tagName === 'LABEL') {
                    textNodes.push(node);
                }
            }
            
            textNodes.forEach(textNode => {
                if (textNode.parentElement && textNode.textContent.includes('*')) {
                    const parent = textNode.parentElement;
                    parent.innerHTML = parent.innerHTML.replace(/\*/g, '<span style="color: #ff0000 !important; font-weight: bold !important;">*</span>');
                }
            });
        }
        
        // Force full width layout
        function forceFullWidth() {
            // Get all main container elements
            const mainContainers = document.querySelectorAll('.main .block-container, .main > div, .block-container');
            mainContainers.forEach(container => {
                container.style.maxWidth = 'none';
                container.style.width = '100%';
            });
            
            // Force data editors and frames to full width
            const dataElements = document.querySelectorAll('.stDataEditor, .stDataFrame, [data-testid="dataframe"]');
            dataElements.forEach(element => {
                element.style.width = '100%';
                element.style.maxWidth = 'none';
            });
        }
        
        // Run immediately and periodically
        setTimeout(forceFullWidth, 100);
        setTimeout(forceFullWidth, 500);
        setTimeout(forceFullWidth, 1000);
        
        // Style asterisks red - run multiple times with different delays
        setTimeout(styleAsterisks, 100);
        setTimeout(styleAsterisks, 200);
        setTimeout(styleAsterisks, 500);
        setTimeout(styleAsterisks, 800);
        setTimeout(styleAsterisks, 1200);
        setTimeout(styleAsterisks, 2000);
        
        // Continue styling on interval
        setInterval(styleAsterisks, 1000);
        
        // Also run when DOM changes
        const observer = new MutationObserver(function(mutations) {
            forceFullWidth();
            styleAsterisks(); // Also style asterisks on DOM changes
        });
        
        // Start observing after a short delay
        setTimeout(() => {
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        }, 1000);
        </script>
    """, unsafe_allow_html=True)

    sheet_names = [
        "Dashboard",
        "Client", "Business Contact Information", "Business Registrations", "Business Owner",
        "Business Profile", "Business Financial Structure", "Market Domestic",
        "Market Export", "Market Import", "Product Service Lines",
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
            "Product Service Lines",
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
    
    else:
        table_key = f"table_data_{selected}"
        col_key = f"table_cols_{selected}"

        # Initialize form state key for Add Entry button control
        form_state_key = f"show_add_entry_form_{selected}"
        if form_state_key not in st.session_state:
            st.session_state[form_state_key] = False

        # Set columns for every sheet
        if selected == "Client":
            columns = [
                "No",
                "Date Created (MM/DD/YYYY)",
                "Status of Client",
                "Specify Level 1.1 and 1.2",
                "Category of Client",
                "Social Classification",
                "Diff/Abled Type",
                "Client is Senior",
                "Client is Indigenous",
                "Level of Digitalization",
                "Digital Tools",
                "MSME Classification",
                "Client Designation",
                "First Name",
                "Middle Name",
                "Last Name",
                "Suffix",
                "Civil Status",
                "Sex",
                "Barangay",
                "District",
                "Zip Code",
                "Address",
                "Landline Number",
                "Fax Number",
                "Mobile Number",
                "Email Address",
                "Social Media",
                "Website",
                "E-Commerce Platform"
            ]
        elif selected == "Business Contact Information":
            columns = [
                "No",
                "Status of Business Registration",
                "Registered Business",
                "Date Registered (MM/DD/YYYY)",
                "Business Company Name",
                "Trade or Billboard Name",
                "IPO Registration Number",
                "Region",
                "Province",
                "City/Municipality",
                "Barangay",
                "District",
                "Zip Code",
                "Address",
                "Latitude",
                "Longitude",
                "Landline Number",
                "Fax Number",
                "Mobile Number",
                "Email Address",
                "E-Commerce Platform",
                "Social Media",
                "Website",
                "Third Party Platform"
            ]
        elif selected == "Business Registrations":
            columns = [
                "No",
                "Name of Business",
                "Registering Agency",
                "Agency Expiry Date (MM/DD/YYYY)",
                "Agency Reg Number",
                "Business Permit",
                "Bus Permit Expiry Date (MM/DD/YYYY)",
                "Bus Permit Reg Number",
                "BIR (TIN) No.",
                "BMBE Registration",
                "BMBE Expiry Date (MM/DD/YYYY)",
                "FDA Reg Number",
                "FDA Expiry Date (MM/DD/YYYY)",
                "Certification Type",
                "Cert/License No",
                "Expiration Date (MM/DD/YYYY)"
            ]
        elif selected == "Business Owner":
            columns = [
                "No",
                "Given Name",
                "Middle Name",
                "Last Name",
                "Suffix",
                "Civil Status",
                "Sex",
                "Birthdate (MM/DD/YYYY)",
                "Birth Year",
                "Citizenship",
                "Social Classification",
                "Diff/Abled type",
                "Owner is Senior",
                "Owner is Indigenous",
                "Region",
                "Province",
                "City/Municipality",
                "Barangay",
                "District",
                "Address"
            ]

            if st.session_state[form_state_key]:
                # Initialize session state for success message
                if 'bo_show_success' not in st.session_state:
                    st.session_state.bo_show_success = False
                    st.session_state.bo_success_timer = 0
                
                # Business Owner form with validation
                st.markdown(f"### Add Entry to {selected}")
                st.markdown("**Fields marked with * are required**")
                
                new_entry = {}
                validation_errors = []
                
                # Define required fields (marked with ; in your specification)
                required_fields = [
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
                citizenships = [""] + sorted(citizenships)  # Add empty option at beginning
                
                # Row 1: Given Name (Required), Middle Name (Optional), Last Name (Required)
                col1, col2, col3 = st.columns(3)
                with col1:
                    # Given Name with red asterisk
                    st.markdown('<label style="color: black;">Given Name <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["Given Name"] = st.text_input(
                        "Given Name *",
                        key=f"bo_given_name_{st.session_state.get('bo_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Middle Name (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Middle Name"] = st.text_input(
                        "Middle Name (Optional)",
                        key=f"bo_middle_name_{st.session_state.get('bo_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    # Last Name with red asterisk
                    st.markdown('<label style="color: black;">Last Name <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["Last Name"] = st.text_input(
                        "Last Name *",
                        key=f"bo_last_name_{st.session_state.get('bo_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 2: Suffix (Optional), Civil Status (Required), Sex (Required)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Suffix (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Suffix"] = st.text_input(
                        "Suffix (Optional)",
                        key=f"bo_suffix_{st.session_state.get('bo_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    # Civil Status with red asterisk
                    st.markdown('<label style="color: black;">Civil Status <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["Civil Status"] = st.text_input(
                        "Civil Status *",
                        key=f"bo_civil_status_{st.session_state.get('bo_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    # Sex with red asterisk
                    st.markdown('<label style="color: black;">Sex <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    sex_options = ["", "Male", "Female"]
                    new_entry["Sex"] = st.selectbox(
                        "Sex *",
                        sex_options,
                        key=f"bo_sex_{st.session_state.get('bo_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 3: Birthdate (Optional), Birth Year (Optional), Citizenship (Required)
                col1, col2, col3 = st.columns(3)
                with col1:
                    birthdate = st.date_input(
                        "Birthdate (Optional)",
                        value=None,
                        key=f"bo_birthdate_{st.session_state.get('bo_form_counter', 0)}"
                    )
                    new_entry["Birthdate (MM/DD/YYYY)"] = birthdate.strftime("%m/%d/%Y") if birthdate else ""
                with col2:
                    st.markdown('<label style="color: black;">Birth Year (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Birth Year"] = st.text_input(
                        "Birth Year (Optional)",
                        key=f"bo_birth_year_{st.session_state.get('bo_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    # Citizenship with red asterisk
                    st.markdown('<label style="color: black;">Citizenship <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["Citizenship"] = st.selectbox(
                        "Citizenship *",
                        citizenships,
                        key=f"bo_citizenship_{st.session_state.get('bo_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 4: Social Classification (Required), Diff/Abled Type (Optional), Owner is Senior (Required)
                col1, col2, col3 = st.columns(3)
                with col1:
                    # Social Classification with red asterisk
                    st.markdown('<label style="color: black;">Social Classification <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    social_options = ["", "Abled", "Person with Disabilities"]
                    new_entry["Social Classification"] = st.selectbox(
                        "Social Classification *",
                        social_options,
                        key=f"bo_social_class_{st.session_state.get('bo_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Diff/Abled Type (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Diff/Abled type"] = st.text_input(
                        "Diff/Abled Type (Optional)",
                        key=f"bo_disabled_type_{st.session_state.get('bo_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    # Owner is Senior with red asterisk
                    st.markdown('<label style="color: black;">Owner is Senior <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    senior_options = ["", "Yes", "No"]
                    new_entry["Owner is Senior"] = st.selectbox(
                        "Owner is Senior *",
                        senior_options,
                        key=f"bo_senior_{st.session_state.get('bo_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 5: Owner is Indigenous (Required)
                col1, col2, col3 = st.columns(3)
                with col1:
                    # Owner is Indigenous with red asterisk
                    st.markdown('<label style="color: black;">Owner is Indigenous <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    indigenous_options = ["", "Yes", "No"]
                    new_entry["Owner is Indigenous"] = st.selectbox(
                        "Owner is Indigenous *",
                        indigenous_options,
                        key=f"bo_indigenous_{st.session_state.get('bo_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.empty()  # Empty column
                with col3:
                    st.empty()  # Empty column
                
                # Location Information Section
                st.markdown("#### Location Information")
                location_data = create_location_widgets()
                new_entry["Region"] = location_data["region"]
                new_entry["Province"] = location_data["province"]
                new_entry["City/Municipality"] = location_data["city"]
                new_entry["Barangay"] = location_data["barangay"]
                
                # Address Information Section
                st.markdown("#### Address Information")
                
                # Row 6: District (Required), Address (Required)
                col1, col2, col3 = st.columns(3)
                with col1:
                    # District with red asterisk
                    st.markdown('<label style="color: black;">District <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["District"] = st.text_input(
                        "District *",
                        key=f"bo_district_{st.session_state.get('bo_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    # Address with red asterisk
                    st.markdown('<label style="color: black;">Address <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["Address"] = st.text_input(
                        "Address *",
                        key=f"bo_address_{st.session_state.get('bo_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.empty()  # Empty column
                
                # Validation logic
                for field in required_fields:
                    value = new_entry.get(field, "")
                    if not value or (isinstance(value, str) and value.strip() == ""):
                        validation_errors.append(field)
                
                # Submit button
                submitted = st.button("Submit")
                
                if submitted:
                    if validation_errors:
                        st.error("Please fill in all required fields marked with *")
                        for field in validation_errors:
                            st.error(f"• {field}")
                    else:
                        # Auto-increment 'No' and ensure order
                        data = st.session_state[table_key]
                        next_no = len(data) + 1
                        row = [str(next_no)]
                        for col in columns[1:]:
                            row.append(new_entry.get(col, ""))
                        data.append(row)
                        st.session_state[table_key] = data
                        save_current_data(selected)
                        
                        st.success("Business Owner saved successfully!")
                        
                        # Clear form fields by incrementing counter
                        if 'bo_form_counter' not in st.session_state:
                            st.session_state.bo_form_counter = 0
                        st.session_state.bo_form_counter += 1
                        
                        # Clear location dropdowns
                        st.session_state.loc_region = None
                        st.session_state.loc_province = None
                        st.session_state.loc_city = None
                        st.session_state.loc_barangay = None
                        
                        # Close form
                        st.session_state[form_state_key] = False
                        st.rerun()
        elif selected == "Business Profile":
            columns = [
                "No",
                "Year Established",
                "Form of Organization",
                "Specify Franchise",
                "Major Activity",
                "Minor Activity",
                "PSIC Group",
                "PSIC Division",
                "PSIC Section",
                "Prio Industry Cluster",
                "Trade Association and Affiliation",
                "Level of Business Operation Date (MM/DD/YYYY)",
                "Growth Tracker",
                "EDT Level",
                "Assisted By",
                "Remarks"
            ]

            if st.session_state[form_state_key]:
                # Business Profile form with validation
                st.markdown(f"### Add Entry to {selected}")
                st.markdown("**Fields marked with * are required**")
                
                new_entry = {}
                validation_errors = []
                
                # Define required fields (marked with ; in your specification)
                required_fields = [
                    "Year Established",
                    "Form of Organization",
                    "Major Activity",
                    "Minor Activity",
                    "PSIC Group",
                    "PSIC Division",
                    "PSIC Section",
                    "Prio Industry Cluster"
                ]
                
                # Row 1: Year Established (Required), Form of Organization (Required), Specify Franchise (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Year Established <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    year_established = st.date_input(
                        "Year Established *",
                        value=None,
                        key=f"bp_year_established_{st.session_state.get('bp_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                    new_entry["Year Established"] = year_established.year if year_established else ""
                with col2:
                    st.markdown('<label style="color: black;">Form of Organization <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    form_options = [
                        "",
                        "Association",
                        "Cooperative", 
                        "Corporation", 
                        "Franchise", 
                        "One Person Corporation", 
                        "Partnership", 
                        "Sole Proprietorship", 
                        "Worker's/Rural's Association (DOLE)"
                    ]
                    new_entry["Form of Organization"] = st.selectbox(
                        "Form of Organization *",
                        form_options,
                        key=f"bp_form_org_{st.session_state.get('bp_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Specify Franchise (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Specify Franchise"] = st.text_input(
                        "Specify Franchise (Optional)",
                        key=f"bp_franchise_{st.session_state.get('bp_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 2: Major Activity (Required), Minor Activity (Required), PSIC Integration
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Major Activity <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    major_activity_options = [
                        "",
                        "Exporting",
                        "Importing",
                        "Manufacturing/Producing",
                        "Retailing/Trading",
                        "Service",
                        "Wholesaling/Trading"
                    ]
                    selected_major_activity = st.selectbox(
                        "Major Activity *",
                        major_activity_options,
                        key=f"bp_major_activity_{st.session_state.get('bp_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                    new_entry["Major Activity"] = selected_major_activity
                with col2:
                    st.markdown('<label style="color: black;">Minor Activity <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    # Auto-populate Minor Activity with Major Activity value
                    new_entry["Minor Activity"] = st.text_input(
                        "Minor Activity *",
                        value=selected_major_activity,  # Automatically set to match Major Activity
                        disabled=True,  # Make it read-only since it auto-populates
                        key=f"bp_minor_activity_{st.session_state.get('bp_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.empty()  # Placeholder for alignment
                
                # Row 3: PSIC Classification (Cascading Dropdowns)
                st.markdown("#### PSIC Classification")
                psic_data = create_psic_widgets()
                new_entry["PSIC Section"] = psic_data["section"]
                new_entry["PSIC Division"] = psic_data["division"]
                new_entry["PSIC Group"] = psic_data["group"]
                
                # Row 4: Prio Industry Cluster (Required), Trade Association (Optional), Level of Business Operation Date (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Prio Industry Cluster <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    prio_industry_options = [
                        "",
                        "Abaca and Abaca Products",
                        "Agribusiness",
                        "Bamboo and Bamboo Products",
                        "Banana",
                        "Cacao",
                        "Coconut and Coconut Products",
                        "Coffee",
                        "Construction",
                        "Creatives",
                        "Dairy",
                        "Fish and Fish Products",
                        "Gifts/Decors and Housewares",
                        "Health and Wellness",
                        "ICT",
                        "Mango and Mango Products",
                        "Milkfish",
                        "Mining",
                        "Not Applicable",
                        "Others",
                        "Palm Oil",
                        "Poultry",
                        "Processed Food",
                        "Processed Fruits and Nuts",
                        "Rubber and Rubber Products",
                        "Seaweed and Seaweeds Products",
                        "Shipbuilding",
                        "Tourism",
                        "Transport",
                        "Tuna",
                        "Wearables & Homestyle",
                        "Wood"
                    ]
                    new_entry["Prio Industry Cluster"] = st.selectbox(
                        "Prio Industry Cluster *",
                        prio_industry_options,
                        key=f"bp_prio_cluster_{st.session_state.get('bp_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Trade Association and Affiliation (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Trade Association and Affiliation"] = st.text_input(
                        "Trade Association and Affiliation (Optional)",
                        key=f"bp_trade_assoc_{st.session_state.get('bp_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Level of Business Operation Date (Optional)</label>', unsafe_allow_html=True)
                    business_op_date = st.date_input(
                        "Level of Business Operation Date (Optional)",
                        value=None,
                        key=f"bp_business_op_date_{st.session_state.get('bp_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                    new_entry["Level of Business Operation Date (MM/DD/YYYY)"] = business_op_date.strftime("%m/%d/%Y") if business_op_date else ""
                
                # Row 5: Growth Tracker (Optional), EDT Level (Optional), Assisted By (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Growth Tracker (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Growth Tracker"] = st.text_input(
                        "Growth Tracker (Optional)",
                        key=f"bp_growth_tracker_{st.session_state.get('bp_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">EDT Level (Optional)</label>', unsafe_allow_html=True)
                    new_entry["EDT Level"] = st.text_input(
                        "EDT Level (Optional)",
                        key=f"bp_edt_level_{st.session_state.get('bp_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Assisted By (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Assisted By"] = st.text_input(
                        "Assisted By (Optional)",
                        key=f"bp_assisted_by_{st.session_state.get('bp_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 6: Remarks (Optional) - Full Width
                st.markdown('<label style="color: black;">Remarks (Optional)</label>', unsafe_allow_html=True)
                new_entry["Remarks"] = st.text_area(
                    "Remarks (Optional)",
                    key=f"bp_remarks_{st.session_state.get('bp_form_counter', 0)}",
                    label_visibility="collapsed"
                )
                
                # Validation logic
                for field in required_fields:
                    value = new_entry.get(field, "")
                    if not value or (isinstance(value, str) and value.strip() == ""):
                        validation_errors.append(field)
                
                # Submit button
                submitted = st.button("Submit")
                
                if submitted:
                    if validation_errors:
                        st.error("Please fill in all required fields marked with *")
                        for field in validation_errors:
                            st.error(f"• {field}")
                    else:
                        # Auto-increment 'No' and ensure order
                        data = st.session_state[table_key]
                        next_no = len(data) + 1
                        row = [str(next_no)]
                        for col in columns[1:]:
                            row.append(new_entry.get(col, ""))
                        data.append(row)
                        st.session_state[table_key] = data
                        save_current_data(selected)
                        
                        st.success("Business Profile saved successfully!")
                        
                        # Clear form fields by incrementing counter
                        if 'bp_form_counter' not in st.session_state:
                            st.session_state.bp_form_counter = 0
                        st.session_state.bp_form_counter += 1
                        
                        # Clear PSIC dropdowns
                        st.session_state.psic_section = ""
                        st.session_state.psic_division = ""
                        st.session_state.psic_group = ""
                        
                        # Close form
                        st.session_state[form_state_key] = False
                        st.rerun()
        elif selected == "Business Financial Structure":
            columns = [
                "No",
                "Initial Capitalization",
                "Capital Structure",
                "Authorize Capital",
                "Subscribed Capital",
                "Paid Up Capital",
                "Capitalization Year",
                "Asset Classification Year",
                "Asset Size Range",
                "Sales History Year",
                "Domestic Sales",
                "Export Sales"
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
        elif selected == "Product Service Lines":
            columns = [
                "No",
                "Product/Service Line",
                "Major Raw Material/s",
                "Year of Production",
                "Valie/Volume of Production",
                "Unit Measure of Production",
                "Certification Type",
                "Certifying Body",
                "Expiry Date (MM/DD/YYYY)"
            ]
        elif selected == "Employment Statistics":
            columns = [
                "No",
                "Year",
                "Fulltime Abled Male",
                "Fulltime Abled Female",
                "Fulltime PWD Male",
                "Fulltime PWD Female",
                "Fulltime Indigenous Male",
                "Fulltime Indigenous Female",
                "Fulltime Senior Male",
                "Fulltime Senior Female",
                "Part-time Abled Male",
                "Part-time Abled Female",
                "Part-time PWD Male",
                "Part-time PWD Female",
                "Part-time Indigenous Male",
                "Part-time Indigenous Female",
                "Part-time Senior Male",
                "Part-time Senior Female"
            ]
        elif selected == "Assistance":
            columns = [
                "No",
                "EDT Assistance Level",
                "Type of Assistance",
                "Sub Type of Assistance",
                "Remarks",
                "Date Start (MM/DD/YYYY)",
                "Date End (MM/DD/YYYY)",
                "MSME Program",
                "MSME Availed (MM/DD/YYYY)",
                "Assisted By",
                "Assisting Office",
                "Type of NC",
                "Location of NC",
                "Assisting Officer Region",
                "Assisting Officer Province",
                "Assisting Officer City",
                "Jobs Generated",
                "Investment Generated",
                "Domestic Sales Generated",
                "Export Sales Generated",
                "Amount Loan Grant",
                "Training – Fund Source",
                "Training – Abled Male",
                "Training – Abled Female",
                "Training – PWD Male",
                "Training – PWD Female",
                "Training – Indigenous Male",
                "Training – Indigenous Female",
                "Training – Senior Male",
                "Training – Senior Female"
            ]
        elif selected == "Jobs Generated":
            columns = [
                "No",
                "Date Recorded (MM/DD/YYYY)",
                "Direct Community Jobs",
                "Indirect Community Jobs",
                "Direct Home Based",
                "Indirect Home Based",
                "Direct Jobs Sustained",
                "Indirect Jobs Sustained"
            ]

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

        # Add Entry Button and Form Handling
        st.markdown("### Data Entry")
        if st.button("Add Entry", key=f"add_entry_btn_{selected}"):
            st.session_state[form_state_key] = True
            st.rerun()

        if st.session_state[form_state_key]:
            if selected == "Client":
                # Initialize session state for success message
                if 'client_show_success' not in st.session_state:
                    st.session_state.client_show_success = False
                    st.session_state.client_success_timer = 0

                # Client form with validation
                st.markdown(f"### Add Entry to {selected}")
                st.markdown("**Fields marked with * are required**")
                
                new_entry = {}
                validation_errors = []
                
                # Define required fields (marked with ; in your specification)
                required_fields = [
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
                    "Mobile Number"
                ]
                
                # Row 1: Date Created (Required), Status of Client (Required), Specify Level (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    # Date Created with red asterisk
                    st.markdown('<label style="color: black;">Date Created <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    date_created = st.date_input(
                        "Date Created *", 
                        key=f"client_date_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                    new_entry["Date Created (MM/DD/YYYY)"] = date_created.strftime("%m/%d/%Y")
                with col2:
                    # Status of Client with red asterisk
                    st.markdown('<label style="color: black;">Status of Client <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    status_options = [
                        "",
                        "Level 0 - Would be or Potential Entrepreneurs",
                        "Level 1 - Nurturing Startup", 
                        "Level 2 - Growing Enterprises (Registered)",
                        "Level 3 - Expanding Enterprises (Registered)",
                        "Level 4 - Sustaining Enterprises"
                    ]
                    new_entry["Status of Client"] = st.selectbox(
                        "Status of Client *",
                        status_options,
                        key=f"client_status_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Specify Level 1.1 and 1.2 (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Specify Level 1.1 and 1.2"] = st.text_input(
                        "Specify Level 1.1 and 1.2 (Optional)", 
                        key=f"client_specify_level_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 2: Category of Client (Required), Social Classification (Required), Diff/Abled Type (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    # Category of Client with red asterisk
                    st.markdown('<label style="color: black;">Category of Client <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    category_options = ["", "Retiree", "Self-Employed", "Senior Citizen", "Student", "Unemployed", "Urban Poor", "Youth"]
                    new_entry["Category of Client"] = st.selectbox(
                        "Category of Client *",
                        category_options,
                        key=f"client_category_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    # Social Classification with red asterisk
                    st.markdown('<label style="color: black;">Social Classification <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    social_options = ["", "Abled", "Person with Disabilities"]
                    new_entry["Social Classification"] = st.selectbox(
                        "Social Classification *",
                        social_options,
                        key=f"client_social_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Diff/Abled Type (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Diff/Abled Type"] = st.text_input(
                        "Diff/Abled Type (Optional)",
                        key=f"client_disabled_type_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 3: Client is Senior (Required), Client is Indigenous (Required), Level of Digitalization (Required)
                col1, col2, col3 = st.columns(3)
                with col1:
                    # Client is Senior with red asterisk
                    st.markdown('<label style="color: black;">Client is Senior <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    senior_options = ["", "Yes", "No"]
                    new_entry["Client is Senior"] = st.selectbox(
                        "Client is Senior *",
                        senior_options,
                        key=f"client_senior_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    # Client is Indigenous with red asterisk
                    st.markdown('<label style="color: black;">Client is Indigenous <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    indigenous_options = ["", "Yes", "No"]
                    new_entry["Client is Indigenous"] = st.selectbox(
                        "Client is Indigenous *",
                        indigenous_options,
                        key=f"client_indigenous_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    # Level of Digitalization with red asterisk
                    st.markdown('<label style="color: black;">Level of Digitalization <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    digital_options = [
                        "",
                        "Level 0 - No use of digital tools",
                        "Level 1 (Basic) - MSMEs that use basic digital tools for business",
                        "Level 2 (Intermediate) - MSMEs that have an online presence",
                        "Level 3 (Advanced) - Use of advanced digital tools"
                    ]
                    new_entry["Level of Digitalization"] = st.selectbox(
                        "Level of Digitalization *",
                        digital_options,
                        key=f"client_digital_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 4: Digital Tools (Optional), MSME Classification (Optional), Client Designation (Required)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Digital Tools (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Digital Tools"] = st.text_input(
                        "Digital Tools (Optional)",
                        key=f"client_digital_tools_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">MSME Classification (Optional)</label>', unsafe_allow_html=True)
                    new_entry["MSME Classification"] = st.text_input(
                        "MSME Classification (Optional)",
                        key=f"client_msme_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    # Client Designation with red asterisk
                    st.markdown('<label style="color: black;">Client Designation <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    designation_options = ["", "Owner", "Representative"]
                    new_entry["Client Designation"] = st.selectbox(
                        "Client Designation *",
                        designation_options,
                        key=f"client_designation_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 5: First Name (Required), Middle Name (Optional), Last Name (Required)
                col1, col2, col3 = st.columns(3)
                with col1:
                    # First Name with red asterisk
                    st.markdown('<label style="color: black;">First Name <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["First Name"] = st.text_input(
                        "First Name *", 
                        key=f"client_first_name_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Middle Name (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Middle Name"] = st.text_input(
                        "Middle Name (Optional)", 
                        key=f"client_middle_name_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    # Last Name with red asterisk
                    st.markdown('<label style="color: black;">Last Name <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["Last Name"] = st.text_input(
                        "Last Name *", 
                        key=f"client_last_name_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 6: Suffix (Optional), Civil Status (Required), Sex (Required)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Suffix (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Suffix"] = st.text_input(
                        "Suffix (Optional)", 
                        key=f"client_suffix_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    # Civil Status with red asterisk
                    st.markdown('<label style="color: black;">Civil Status <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["Civil Status"] = st.text_input(
                        "Civil Status *", 
                        key=f"client_civil_status_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    # Sex with red asterisk
                    st.markdown('<label style="color: black;">Sex <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    sex_options = ["", "Male", "Female"]
                    new_entry["Sex"] = st.selectbox(
                        "Sex *",
                        sex_options,
                        key=f"client_sex_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 7: Barangay (Required), District (Required), Zip Code (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    # Barangay with red asterisk
                    st.markdown('<label style="color: black;">Barangay <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["Barangay"] = st.text_input(
                        "Barangay *", 
                        key=f"client_barangay_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    # District with red asterisk
                    st.markdown('<label style="color: black;">District <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["District"] = st.text_input(
                        "District *", 
                        key=f"client_district_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Zip Code (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Zip Code"] = st.text_input(
                        "Zip Code (Optional)", 
                        key=f"client_zip_code_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 8: Address (Optional), Landline Number (Optional), Fax Number (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Address (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Address"] = st.text_input(
                        "Address (Optional)", 
                        key=f"client_address_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Landline Number (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Landline Number"] = st.text_input(
                        "Landline Number (Optional)", 
                        key=f"client_landline_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Fax Number (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Fax Number"] = st.text_input(
                        "Fax Number (Optional)", 
                        key=f"client_fax_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 9: Mobile Number (Required), Email Address (Optional), Social Media (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    # Mobile Number with red asterisk
                    st.markdown('<label style="color: black;">Mobile Number <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["Mobile Number"] = st.text_input(
                        "Mobile Number *", 
                        key=f"client_mobile_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Email Address (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Email Address"] = st.text_input(
                        "Email Address (Optional)", 
                        key=f"client_email_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Social Media (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Social Media"] = st.text_input(
                        "Social Media (Optional)", 
                        key=f"client_social_media_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 10: Website (Optional), E-Commerce Platform (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Website (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Website"] = st.text_input(
                        "Website (Optional)", 
                        key=f"client_website_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">E-Commerce Platform (Optional)</label>', unsafe_allow_html=True)
                    new_entry["E-Commerce Platform"] = st.text_input(
                        "E-Commerce Platform (Optional)", 
                        key=f"client_ecommerce_{st.session_state.get('client_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.empty()  # Empty column for alignment
                
                # Validation logic
                for field in required_fields:
                    if field in new_entry and (not new_entry[field] or new_entry[field] == ""):
                        validation_errors.append(field)
                
                # Submit button
                submitted = st.button("Submit")
                
                if submitted:
                    if validation_errors:
                        st.error("Please fill in all required fields marked with *")
                        for field in validation_errors:
                            st.error(f"Missing: {field}")
                    else:
                        # Auto-increment 'No' and ensure order
                        data = st.session_state[table_key]
                        next_no = len(data) + 1
                        row = [str(next_no)]
                        for col in columns[1:]:
                            row.append(new_entry.get(col, ""))
                        data.append(row)
                        st.session_state[table_key] = data
                        save_current_data(selected)
                        
                        st.success("Client information saved successfully!")
                        
                        # Clear form fields by incrementing counter
                        if 'client_form_counter' not in st.session_state:
                            st.session_state.client_form_counter = 0
                        st.session_state.client_form_counter += 1
                        
                        # Close form
                        st.session_state[form_state_key] = False
                        st.rerun()

            elif selected == "Business Contact Information":
                st.markdown(f"### Add Entry to {selected}")
                
                # Initialize required fields and validation
                required_fields = [
                    "Status of Business Registration",
                    "Region", 
                    "Province",
                    "City/Municipality", 
                    "Barangay",
                    "Mobile Number"
                ]
                validation_errors = []
                new_entry = {}
                
                # Row 1: Status of Business Registration, Registered Business, Date Registered
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="font-size: 14px; font-weight: 400; color: rgb(38, 39, 48);">Status of Business Registration <span style="color: #ff0000; font-weight: bold;">*</span></label>', unsafe_allow_html=True)
                    new_entry["Status of Business Registration"] = st.selectbox(
                        "Status of Business Registration",
                        ["", "Registered", "Unregistered"],
                        key=f"bci_status_{st.session_state.get('bci_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="font-size: 14px; font-weight: 400; color: rgb(38, 39, 48);">Registered Business (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Registered Business"] = st.text_input(
                        "Registered Business",
                        key=f"bci_reg_business_{st.session_state.get('bci_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="font-size: 14px; font-weight: 400; color: rgb(38, 39, 48);">Date Registered (Optional)</label>', unsafe_allow_html=True)
                    date_registered = st.date_input(
                        "Date Registered",
                        value=None,
                        key=f"bci_date_reg_{st.session_state.get('bci_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                    if date_registered:
                        new_entry["Date Registered (MM/DD/YYYY)"] = date_registered.strftime("%m/%d/%Y")
                    else:
                        new_entry["Date Registered (MM/DD/YYYY)"] = ""
                
                # Row 2: Business Company Name, Trade or Billboard Name, IPO Registration Number
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_entry["Business Company Name"] = st.text_input(
                        "Business Company Name (Optional)",
                        key=f"bci_company_name_{st.session_state.get('bci_form_counter', 0)}"
                    )
                with col2:
                    new_entry["Trade or Billboard Name"] = st.text_input(
                        "Trade or Billboard Name (Optional)",
                        key=f"bci_trade_name_{st.session_state.get('bci_form_counter', 0)}"
                    )
                with col3:
                    new_entry["IPO Registration Number"] = st.text_input(
                        "IPO Registration Number (Optional)",
                        key=f"bci_ipo_number_{st.session_state.get('bci_form_counter', 0)}"
                    )
                
                # Location Information using create_location_widgets
                st.markdown("#### Location Information")
                location_data = create_location_widgets()
                new_entry["Region"] = location_data["region"]
                new_entry["Province"] = location_data["province"]
                new_entry["City/Municipality"] = location_data["city"]
                new_entry["Barangay"] = location_data["barangay"]
                
                # Row 3: District, Zip Code, Address
                col1, col2, col3 = st.columns(3)
                with col1:
                    # District with red asterisk
                    st.markdown('<label style="color: black;">District <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["District"] = st.text_input(
                        "District *",
                        key=f"bci_district_{st.session_state.get('bci_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    new_entry["Zip Code"] = st.text_input(
                        "Zip Code (Optional)",
                        key=f"bci_zip_code_{st.session_state.get('bci_form_counter', 0)}"
                    )
                with col3:
                    new_entry["Address"] = st.text_input(
                        "Address (Optional)",
                        key=f"bci_address_{st.session_state.get('bci_form_counter', 0)}"
                    )
                
                # Row 4: Latitude, Longitude, Landline Number
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_entry["Latitude"] = st.text_input(
                        "Latitude (Optional)",
                        key=f"bci_latitude_{st.session_state.get('bci_form_counter', 0)}"
                    )
                with col2:
                    new_entry["Longitude"] = st.text_input(
                        "Longitude (Optional)",
                        key=f"bci_longitude_{st.session_state.get('bci_form_counter', 0)}"
                    )
                with col3:
                    new_entry["Landline Number"] = st.text_input(
                        "Landline Number (Optional)",
                        key=f"bci_landline_{st.session_state.get('bci_form_counter', 0)}"
                    )
                
                # Row 5: Fax Number, Mobile Number, Email Address
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="font-size: 14px; font-weight: 400; color: rgb(38, 39, 48);">Fax Number (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Fax Number"] = st.text_input(
                        "Fax Number",
                        key=f"bci_fax_{st.session_state.get('bci_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="font-size: 14px; font-weight: 400; color: rgb(38, 39, 48);">Mobile Number <span style="color: #ff0000; font-weight: bold;">*</span></label>', unsafe_allow_html=True)
                    new_entry["Mobile Number"] = st.text_input(
                        "Mobile Number",
                        key=f"bci_mobile_{st.session_state.get('bci_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="font-size: 14px; font-weight: 400; color: rgb(38, 39, 48);">Email Address (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Email Address"] = st.text_input(
                        "Email Address",
                        key=f"bci_email_{st.session_state.get('bci_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 6: E-Commerce Platform, Social Media, Website
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_entry["E-Commerce Platform"] = st.text_input(
                        "E-Commerce Platform (Optional)",
                        key=f"bci_ecommerce_{st.session_state.get('bci_form_counter', 0)}"
                    )
                with col2:
                    new_entry["Social Media"] = st.text_input(
                        "Social Media (Optional)",
                        key=f"bci_social_media_{st.session_state.get('bci_form_counter', 0)}"
                    )
                with col3:
                    new_entry["Website"] = st.text_input(
                        "Website (Optional)",
                        key=f"bci_website_{st.session_state.get('bci_form_counter', 0)}"
                    )
                
                # Row 7: Third Party Platform
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_entry["Third Party Platform"] = st.text_input(
                        "Third Party Platform (Optional)",
                        key=f"bci_third_party_{st.session_state.get('bci_form_counter', 0)}"
                    )
                with col2:
                    st.empty()  # Empty column
                with col3:
                    st.empty()  # Empty column
                
                # Validation logic
                for field in required_fields:
                    if field in new_entry and (not new_entry[field] or new_entry[field] == ""):
                        validation_errors.append(field)
                
                # Submit button
                submitted = st.button("Submit")
                
                if submitted:
                    if validation_errors:
                        st.error("Please fill in all required fields before submitting.")
                    else:
                        # Auto-increment 'No' and ensure order
                        data = st.session_state[table_key]
                        next_no = len(data) + 1
                        row = [str(next_no)]
                        for col in columns[1:]:
                            row.append(new_entry.get(col, ""))
                        data.append(row)
                        st.session_state[table_key] = data
                        save_current_data(selected)
                        
                        st.success("Business Contact Information saved successfully!")
                        
                        # Clear form fields by incrementing counter
                        if 'bci_form_counter' not in st.session_state:
                            st.session_state.bci_form_counter = 0
                        st.session_state.bci_form_counter += 1
                        
                        # Close form
                        st.session_state[form_state_key] = False
                        st.rerun()
                        st.session_state.bci_success_timer = 0

            elif selected == "Business Registrations":
                st.markdown(f"### Add Entry to {selected}")
                
                # Initialize required fields and validation
                required_fields = [
                    "Name of Business",
                    "Registering Agency",
                    "Agency Expiry Date (MM/DD/YYYY)",
                    "Agency Reg Number"
                ]
                validation_errors = []
                new_entry = {}
                
                # Row 1: Name of Business (Required), Registering Agency (Required), Agency Expiry Date (Required)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Name of Business <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["Name of Business"] = st.text_input(
                        "Name of Business *",
                        key=f"br_name_{st.session_state.get('br_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Registering Agency <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["Registering Agency"] = st.text_input(
                        "Registering Agency *",
                        key=f"br_agency_{st.session_state.get('br_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Agency Expiry Date <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    agency_expiry = st.date_input(
                        "Agency Expiry Date *",
                        value=None,
                        key=f"br_agency_expiry_{st.session_state.get('br_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                    new_entry["Agency Expiry Date (MM/DD/YYYY)"] = agency_expiry.strftime("%m/%d/%Y") if agency_expiry else ""
                
                # Row 2: Agency Reg Number (Required), Business Permit (Optional), Bus Permit Expiry Date (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Agency Reg Number <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["Agency Reg Number"] = st.text_input(
                        "Agency Reg Number *",
                        key=f"br_agency_reg_{st.session_state.get('br_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Business Permit (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Business Permit"] = st.text_input(
                        "Business Permit",
                        key=f"br_bus_permit_{st.session_state.get('br_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Bus Permit Expiry Date (Optional)</label>', unsafe_allow_html=True)
                    bus_permit_expiry = st.date_input(
                        "Bus Permit Expiry Date",
                        value=None,
                        key=f"br_bus_permit_expiry_{st.session_state.get('br_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                    new_entry["Bus Permit Expiry Date (MM/DD/YYYY)"] = bus_permit_expiry.strftime("%m/%d/%Y") if bus_permit_expiry else ""
                
                # Row 3: Bus Permit Reg Number (Optional), BIR (TIN) No. (Optional), BMBE Registration (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Bus Permit Reg Number (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Bus Permit Reg Number"] = st.text_input(
                        "Bus Permit Reg Number",
                        key=f"br_bus_permit_reg_{st.session_state.get('br_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">BIR (TIN) No. (Optional)</label>', unsafe_allow_html=True)
                    new_entry["BIR (TIN) No."] = st.text_input(
                        "BIR (TIN) No.",
                        key=f"br_tin_{st.session_state.get('br_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">BMBE Registration (Optional)</label>', unsafe_allow_html=True)
                    new_entry["BMBE Registration"] = st.text_input(
                        "BMBE Registration",
                        key=f"br_bmbe_{st.session_state.get('br_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 4: BMBE Expiry Date (Optional), FDA Reg Number (Optional), FDA Expiry Date (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">BMBE Expiry Date (Optional)</label>', unsafe_allow_html=True)
                    bmbe_expiry = st.date_input(
                        "BMBE Expiry Date",
                        value=None,
                        key=f"br_bmbe_expiry_{st.session_state.get('br_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                    new_entry["BMBE Expiry Date (MM/DD/YYYY)"] = bmbe_expiry.strftime("%m/%d/%Y") if bmbe_expiry else ""
                with col2:
                    st.markdown('<label style="color: black;">FDA Reg Number (Optional)</label>', unsafe_allow_html=True)
                    new_entry["FDA Reg Number"] = st.text_input(
                        "FDA Reg Number",
                        key=f"br_fda_reg_{st.session_state.get('br_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">FDA Expiry Date (Optional)</label>', unsafe_allow_html=True)
                    fda_expiry = st.date_input(
                        "FDA Expiry Date",
                        value=None,
                        key=f"br_fda_expiry_{st.session_state.get('br_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                    new_entry["FDA Expiry Date (MM/DD/YYYY)"] = fda_expiry.strftime("%m/%d/%Y") if fda_expiry else ""
                
                # Row 5: Certification Type (Optional), Cert/License No (Optional), Expiration Date (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Certification Type (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Certification Type"] = st.text_input(
                        "Certification Type",
                        key=f"br_cert_type_{st.session_state.get('br_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Cert/License No (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Cert/License No"] = st.text_input(
                        "Cert/License No",
                        key=f"br_cert_license_{st.session_state.get('br_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Expiration Date (Optional)</label>', unsafe_allow_html=True)
                    expiration_date = st.date_input(
                        "Expiration Date",
                        value=None,
                        key=f"br_expiration_{st.session_state.get('br_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                    new_entry["Expiration Date (MM/DD/YYYY)"] = expiration_date.strftime("%m/%d/%Y") if expiration_date else ""
                
                # Validation logic
                for field in required_fields:
                    if field in new_entry and (not new_entry[field] or new_entry[field] == ""):
                        validation_errors.append(field)
                
                # Submit button
                submitted = st.button("Submit")
                
                if submitted:
                    if validation_errors:
                        st.error("Please fill in all required fields marked with *")
                        for field in validation_errors:
                            st.error(f"Missing: {field}")
                    else:
                        # Auto-increment 'No' and ensure order
                        data = st.session_state[table_key]
                        next_no = len(data) + 1
                        row = [str(next_no)]
                        for col in columns[1:]:
                            row.append(new_entry.get(col, ""))
                        data.append(row)
                        st.session_state[table_key] = data
                        save_current_data(selected)
                        
                        st.success("Business Registration saved successfully!")
                        
                        # Clear form fields by incrementing counter
                        if 'br_form_counter' not in st.session_state:
                            st.session_state.br_form_counter = 0
                        st.session_state.br_form_counter += 1
                        
                        # Close form
                        st.session_state[form_state_key] = False
                        st.rerun()
                        
            elif selected == "Business Financial Structure":
                st.markdown(f"### Add Entry to {selected}")
                
                # Initialize required fields and validation
                required_fields = [
                    "Asset Classification Year",
                    "Asset Size Range",
                    "Sales History Year",
                    "Domestic Sales"
                ]
                validation_errors = []
                new_entry = {}
                
                # Row 1: Initial Capitalization (Optional), Capital Structure (Optional), Authorize Capital (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Initial Capitalization (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Initial Capitalization"] = st.text_input(
                        "Initial Capitalization",
                        key=f"bfs_initial_cap_{st.session_state.get('bfs_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Capital Structure (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Capital Structure"] = st.text_input(
                        "Capital Structure",
                        key=f"bfs_capital_structure_{st.session_state.get('bfs_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Authorize Capital (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Authorize Capital"] = st.text_input(
                        "Authorize Capital",
                        key=f"bfs_authorize_cap_{st.session_state.get('bfs_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 2: Subscribed Capital (Optional), Paid Up Capital (Optional), Capitalization Year (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Subscribed Capital (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Subscribed Capital"] = st.text_input(
                        "Subscribed Capital",
                        key=f"bfs_subscribed_cap_{st.session_state.get('bfs_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Paid Up Capital (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Paid Up Capital"] = st.text_input(
                        "Paid Up Capital",
                        key=f"bfs_paid_up_cap_{st.session_state.get('bfs_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Capitalization Year (Optional)</label>', unsafe_allow_html=True)
                    # Year dropdown from 2015-2035
                    year_options = [""] + [str(year) for year in range(2015, 2036)]
                    new_entry["Capitalization Year"] = st.selectbox(
                        "Capitalization Year",
                        year_options,
                        key=f"bfs_cap_year_{st.session_state.get('bfs_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 3: Asset Classification Year (Required), Asset Size Range (Required), Sales History Year (Required)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Asset Classification Year <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    # Year dropdown from 2015-2035
                    year_options = [""] + [str(year) for year in range(2015, 2036)]
                    new_entry["Asset Classification Year"] = st.selectbox(
                        "Asset Classification Year *",
                        year_options,
                        key=f"bfs_asset_year_{st.session_state.get('bfs_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Asset Size Range <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["Asset Size Range"] = st.text_input(
                        "Asset Size Range *",
                        key=f"bfs_asset_range_{st.session_state.get('bfs_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Sales History Year <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    # Year dropdown from 2015-2035
                    year_options = [""] + [str(year) for year in range(2015, 2036)]
                    new_entry["Sales History Year"] = st.selectbox(
                        "Sales History Year *",
                        year_options,
                        key=f"bfs_sales_year_{st.session_state.get('bfs_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 4: Domestic Sales (Required), Export Sales (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Domestic Sales <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["Domestic Sales"] = st.text_input(
                        "Domestic Sales *",
                        key=f"bfs_domestic_sales_{st.session_state.get('bfs_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Export Sales (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Export Sales"] = st.text_input(
                        "Export Sales",
                        key=f"bfs_export_sales_{st.session_state.get('bfs_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Validate required fields
                for field in required_fields:
                    if not new_entry.get(field, "").strip():
                        validation_errors.append(field)
                
                # Submit button
                submitted = st.button("Submit", key="bfs_submit")
                
                if submitted:
                    if validation_errors:
                        st.error("Please fill in all required fields marked with *")
                        for field in validation_errors:
                            st.error(f"Missing: {field}")
                    else:
                        # Auto-increment 'No' and ensure order
                        data = st.session_state[table_key]
                        next_no = len(data) + 1
                        row = [str(next_no)]
                        for col in columns[1:]:
                            row.append(new_entry.get(col, ""))
                        data.append(row)
                        st.session_state[table_key] = data
                        save_current_data(selected)
                        
                        st.success("Business Financial Structure saved successfully!")
                        
                        # Clear form fields by incrementing counter
                        if 'bfs_form_counter' not in st.session_state:
                            st.session_state.bfs_form_counter = 0
                        st.session_state.bfs_form_counter += 1
                        
                        # Close form
                        st.session_state[form_state_key] = False
                        st.rerun()
                        
            elif selected == "Market Domestic":
                st.markdown(f"### Add Entry to {selected}")
                
                # Initialize required fields and validation
                required_fields = [
                    "Product/Service",
                    "Region",
                    "Province"
                ]
                validation_errors = []
                new_entry = {}
                
                # Row 1: Product/Service (Required)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Product/Service <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["Product/Service"] = st.text_input(
                        "Product/Service *",
                        key=f"md_product_service_{st.session_state.get('md_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Location Information using create_location_widgets
                st.markdown("#### Location Information")
                location_data = create_location_widgets()
                new_entry["Region"] = location_data["region"]
                new_entry["Province"] = location_data["province"]
                
                # Validate required fields
                for field in required_fields:
                    if field in ["Region", "Province"]:
                        # For location fields, check the location_data
                        field_key = field.lower()
                        if not location_data.get(field_key, "").strip():
                            validation_errors.append(field)
                    else:
                        if not new_entry.get(field, "").strip():
                            validation_errors.append(field)
                
                # Submit button
                submitted = st.button("Submit", key="md_submit")
                
                if submitted:
                    if validation_errors:
                        st.error("Please fill in all required fields marked with *")
                        for field in validation_errors:
                            st.error(f"Missing: {field}")
                    else:
                        # Auto-increment 'No' and ensure order
                        data = st.session_state[table_key]
                        next_no = len(data) + 1
                        row = [str(next_no)]
                        for col in columns[1:]:
                            row.append(new_entry.get(col, ""))
                        data.append(row)
                        st.session_state[table_key] = data
                        save_current_data(selected)
                        
                        st.success("Market Domestic saved successfully!")
                        
                        # Clear form fields by incrementing counter
                        if 'md_form_counter' not in st.session_state:
                            st.session_state.md_form_counter = 0
                        st.session_state.md_form_counter += 1
                        
                        # Close form
                        st.session_state[form_state_key] = False
                        st.rerun()
                        
            elif selected == "Market Export":
                st.markdown(f"### Add Entry to {selected}")
                
                # All fields are optional (no required fields)
                validation_errors = []
                new_entry = {}
                
                # Row 1: Year Export Started (Optional), Product Service (Optional), Country (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Year Export Started (Optional)</label>', unsafe_allow_html=True)
                    # Year dropdown from 2015-2035 (similar to other year fields)
                    year_options = [""] + [str(year) for year in range(2015, 2036)]
                    new_entry["Year Export Started"] = st.selectbox(
                        "Year Export Started",
                        year_options,
                        key=f"me_year_started_{st.session_state.get('me_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Product Service (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Product Service"] = st.text_input(
                        "Product Service",
                        key=f"me_product_service_{st.session_state.get('me_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Country (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Country"] = st.text_input(
                        "Country",
                        key=f"me_country_{st.session_state.get('me_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 2: Trade Bloc (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Trade Bloc (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Trade Bloc"] = st.text_input(
                        "Trade Bloc",
                        key=f"me_trade_bloc_{st.session_state.get('me_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Submit button (no validation needed since all fields are optional)
                submitted = st.button("Submit", key="me_submit")
                
                if submitted:
                    # Auto-increment 'No' and ensure order
                    data = st.session_state[table_key]
                    next_no = len(data) + 1
                    row = [str(next_no)]
                    for col in columns[1:]:
                        row.append(new_entry.get(col, ""))
                    data.append(row)
                    st.session_state[table_key] = data
                    save_current_data(selected)
                    
                    st.success("Market Export saved successfully!")
                    
                    # Clear form fields by incrementing counter
                    if 'me_form_counter' not in st.session_state:
                        st.session_state.me_form_counter = 0
                    st.session_state.me_form_counter += 1
                    
                    # Close form
                    st.session_state[form_state_key] = False
                    st.rerun()
                    
            elif selected == "Market Import":
                st.markdown(f"### Add Entry to {selected}")
                
                # All fields are optional (no required fields)
                validation_errors = []
                new_entry = {}
                
                # Row 1: Year Import Started (Optional), Product Service (Optional), Country (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Year Import Started (Optional)</label>', unsafe_allow_html=True)
                    # Year dropdown from 2015-2035 (similar to other year fields)
                    year_options = [""] + [str(year) for year in range(2015, 2036)]
                    new_entry["Year Import Started"] = st.selectbox(
                        "Year Import Started",
                        year_options,
                        key=f"mi_year_started_{st.session_state.get('mi_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Product Service (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Product Service"] = st.text_input(
                        "Product Service",
                        key=f"mi_product_service_{st.session_state.get('mi_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Country (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Country"] = st.text_input(
                        "Country",
                        key=f"mi_country_{st.session_state.get('mi_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Submit button (no validation needed since all fields are optional)
                submitted = st.button("Submit", key="mi_submit")
                
                if submitted:
                    # Auto-increment 'No' and ensure order
                    data = st.session_state[table_key]
                    next_no = len(data) + 1
                    row = [str(next_no)]
                    for col in columns[1:]:
                        row.append(new_entry.get(col, ""))
                    data.append(row)
                    st.session_state[table_key] = data
                    save_current_data(selected)
                    
                    st.success("Market Import saved successfully!")
                    
                    # Clear form fields by incrementing counter
                    if 'mi_form_counter' not in st.session_state:
                        st.session_state.mi_form_counter = 0
                    st.session_state.mi_form_counter += 1
                    
                    # Close form
                    st.session_state[form_state_key] = False
                    st.rerun()
                    
            elif selected == "Product Service Lines":
                st.markdown(f"### Add Entry to {selected}")
                
                # Initialize required fields and validation
                required_fields = [
                    "Product/Service Line",
                    "Major Raw Material/s"
                ]
                validation_errors = []
                new_entry = {}
                
                # Row 1: Product/Service Line (Required), Major Raw Material/s (Required), Year of Production (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Product/Service Line <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["Product/Service Line"] = st.text_input(
                        "Product/Service Line *",
                        key=f"psl_product_line_{st.session_state.get('psl_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Major Raw Material/s <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["Major Raw Material/s"] = st.text_input(
                        "Major Raw Material/s *",
                        key=f"psl_raw_materials_{st.session_state.get('psl_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Year of Production (Optional)</label>', unsafe_allow_html=True)
                    # Year dropdown from 2015-2035
                    year_options = [""] + [str(year) for year in range(2015, 2036)]
                    new_entry["Year of Production"] = st.selectbox(
                        "Year of Production",
                        year_options,
                        key=f"psl_year_production_{st.session_state.get('psl_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 2: Valie/Volume of Production (Optional), Unit Measure of Production (Optional), Certification Type (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Valie/Volume of Production (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Valie/Volume of Production"] = st.text_input(
                        "Valie/Volume of Production",
                        key=f"psl_volume_production_{st.session_state.get('psl_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Unit Measure of Production (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Unit Measure of Production"] = st.text_input(
                        "Unit Measure of Production",
                        key=f"psl_unit_measure_{st.session_state.get('psl_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Certification Type (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Certification Type"] = st.text_input(
                        "Certification Type",
                        key=f"psl_cert_type_{st.session_state.get('psl_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 3: Certifying Body (Optional), Expiry Date (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Certifying Body (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Certifying Body"] = st.text_input(
                        "Certifying Body",
                        key=f"psl_cert_body_{st.session_state.get('psl_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Expiry Date (Optional)</label>', unsafe_allow_html=True)
                    expiry_date = st.date_input(
                        "Expiry Date",
                        value=None,
                        key=f"psl_expiry_date_{st.session_state.get('psl_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                    new_entry["Expiry Date (MM/DD/YYYY)"] = expiry_date.strftime("%m/%d/%Y") if expiry_date else ""
                
                # Validate required fields
                for field in required_fields:
                    if not new_entry.get(field, "").strip():
                        validation_errors.append(field)
                
                # Submit button
                submitted = st.button("Submit", key="psl_submit")
                
                if submitted:
                    if validation_errors:
                        st.error("Please fill in all required fields marked with *")
                        for field in validation_errors:
                            st.error(f"Missing: {field}")
                    else:
                        # Auto-increment 'No' and ensure order
                        data = st.session_state[table_key]
                        next_no = len(data) + 1
                        row = [str(next_no)]
                        for col in columns[1:]:
                            row.append(new_entry.get(col, ""))
                        data.append(row)
                        st.session_state[table_key] = data
                        save_current_data(selected)
                        
                        st.success("Product Service Lines saved successfully!")
                        
                        # Clear form fields by incrementing counter
                        if 'psl_form_counter' not in st.session_state:
                            st.session_state.psl_form_counter = 0
                        st.session_state.psl_form_counter += 1
                        
                        # Close form
                        st.session_state[form_state_key] = False
                        st.rerun()
                        
            elif selected == "Employment Statistics":
                st.markdown(f"### Add Entry to {selected}")
                
                # All fields are optional except Year
                required_fields = ["Year"]
                validation_errors = []
                new_entry = {}
                
                # Row 1: Year (Required)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Year <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    # Year dropdown from 2015-2035
                    year_options = [""] + [str(year) for year in range(2015, 2036)]
                    new_entry["Year"] = st.selectbox(
                        "Year *",
                        year_options,
                        key=f"es_year_{st.session_state.get('es_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Employment categories with checkboxes
                st.markdown("#### Employment Categories")
                st.markdown("*Check all that apply to indicate employment status*")
                
                checkbox_columns = [
                    "Fulltime Abled Male", "Fulltime Abled Female",
                    "Fulltime PWD Male", "Fulltime PWD Female", 
                    "Fulltime Indigenous Male", "Fulltime Indigenous Female",
                    "Fulltime Senior Male", "Fulltime Senior Female",
                    "Part-time Abled Male", "Part-time Abled Female",
                    "Part-time PWD Male", "Part-time PWD Female",
                    "Part-time Indigenous Male", "Part-time Indigenous Female", 
                    "Part-time Senior Male", "Part-time Senior Female"
                ]
                
                # Organize checkboxes in rows
                for i in range(0, len(checkbox_columns), 3):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if i < len(checkbox_columns):
                            new_entry[checkbox_columns[i]] = st.checkbox(
                                checkbox_columns[i], 
                                key=f"es_{checkbox_columns[i].replace(' ', '_').lower()}_{st.session_state.get('es_form_counter', 0)}"
                            )
                        else:
                            new_entry[checkbox_columns[i]] = False
                    with col2:
                        if i + 1 < len(checkbox_columns):
                            new_entry[checkbox_columns[i + 1]] = st.checkbox(
                                checkbox_columns[i + 1], 
                                key=f"es_{checkbox_columns[i + 1].replace(' ', '_').lower()}_{st.session_state.get('es_form_counter', 0)}"
                            )
                        else:
                            if i + 1 < len(checkbox_columns):
                                new_entry[checkbox_columns[i + 1]] = False
                    with col3:
                        if i + 2 < len(checkbox_columns):
                            new_entry[checkbox_columns[i + 2]] = st.checkbox(
                                checkbox_columns[i + 2], 
                                key=f"es_{checkbox_columns[i + 2].replace(' ', '_').lower()}_{st.session_state.get('es_form_counter', 0)}"
                            )
                        else:
                            if i + 2 < len(checkbox_columns):
                                new_entry[checkbox_columns[i + 2]] = False
                
                # Validate required fields
                for field in required_fields:
                    if not new_entry.get(field, "").strip():
                        validation_errors.append(field)
                
                # Submit button
                submitted = st.button("Submit", key="es_submit")
                
                if submitted:
                    if validation_errors:
                        st.error("Please fill in all required fields marked with *")
                        for field in validation_errors:
                            st.error(f"Missing: {field}")
                    else:
                        # Auto-increment 'No' and ensure order
                        data = st.session_state[table_key]
                        next_no = len(data) + 1
                        row = [str(next_no), str(new_entry["Year"])]
                        for col in checkbox_columns:
                            row.append("Yes" if new_entry.get(col, False) else "No")
                        data.append(row)
                        st.session_state[table_key] = data
                        save_current_data(selected)
                        
                        st.success("Employment Statistics saved successfully!")
                        
                        # Clear form fields by incrementing counter
                        if 'es_form_counter' not in st.session_state:
                            st.session_state.es_form_counter = 0
                        st.session_state.es_form_counter += 1
                        
                        # Close form
                        st.session_state[form_state_key] = False
                        st.rerun()
                        
            elif selected == "Assistance":
                st.markdown(f"### Add Entry to {selected}")
                
                # Initialize required fields and validation
                required_fields = [
                    "EDT Assistance Level",
                    "Type of Assistance", 
                    "Sub Type of Assistance",
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
                validation_errors = []
                new_entry = {}
                
                # Row 1: EDT Assistance Level (Required), Type of Assistance (Required), Sub Type of Assistance (Required)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">EDT Assistance Level <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    edt_level_options = [
                        "",
                        "Level 0 - Entrepreneurial Mind Setting",
                        "Level 1.1 - Nurturing Start Up (Not Registered)",
                        "Level 1.2 - Nurturing Start Up (Partially Registered)",
                        "Level 2 - Growing Enterprises",
                        "Level 3 - Expanding Enterprises",
                        "Level 4 - Sustaining Enterprises"
                    ]
                    new_entry["EDT Assistance Level"] = st.selectbox(
                        "EDT Assistance Level *",
                        edt_level_options,
                        key=f"ast_edt_level_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Type of Assistance <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    type_assistance_options = [
                        "",
                        "Access to Finance",
                        "Access to Markets",
                        "Advocacy",
                        "Business Registration/Facilitation",
                        "Consumer Related Assistance",
                        "Ecommerce/MSME Digitalization",
                        "Investment Promotion",
                        "Product Development",
                        "Production",
                        "Training and Seminar"
                    ]
                    new_entry["Type of Assistance"] = st.selectbox(
                        "Type of Assistance *",
                        type_assistance_options,
                        key=f"ast_type_assistance_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Sub Type of Assistance <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    sub_type_assistance_options = [
                        "",
                        "BN Registration",
                        "SEC Registration", 
                        "CDA Registration",
                        "DOLE Registration",
                        "BMBE Registration",
                        "LGU/Mayor's Permit",
                        "FDA Registration",
                        "Other Permits",
                        "Other Facilitation Registration Rendered"
                    ]
                    new_entry["Sub Type of Assistance"] = st.selectbox(
                        "Sub Type of Assistance *",
                        sub_type_assistance_options,
                        key=f"ast_sub_type_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 2: Remarks (Required), Date Start (Required), Date End (Required)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Remarks <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["Remarks"] = st.text_area(
                        "Remarks *",
                        key=f"ast_remarks_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Date Start <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    date_start = st.date_input(
                        "Date Start *",
                        value=None,
                        key=f"ast_date_start_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                    new_entry["Date Start (MM/DD/YYYY)"] = date_start.strftime("%m/%d/%Y") if date_start else ""
                with col3:
                    st.markdown('<label style="color: black;">Date End <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    date_end = st.date_input(
                        "Date End *",
                        value=None,
                        key=f"ast_date_end_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                    new_entry["Date End (MM/DD/YYYY)"] = date_end.strftime("%m/%d/%Y") if date_end else ""
                
                # Row 3: MSME Program (Required), MSME Availed (Required), Assisted By (Required)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">MSME Program <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    msme_program_options = [
                        "",
                        "Go Lokal",
                        "Great Women Project",
                        "Green Economic Development (GED)",
                        "Industry Cluster Enhancement (ICE) Program",
                        "Integrated Natural Resources Environmental Management Project - Livelihood Enhancement Support (INREMP-LES) 2",
                        "Kapatid Mentor Me Project (KMME)",
                        "Livelihood Seeding Program - Negosyo Serbisyo Sa Barangay (LSP-NSB)",
                        "Manila FAME",
                        "MSME Digitalization",
                        "MSME Resilience",
                        "MSME Start-up Program",
                        "National Trade Fair (NTF)",
                        "Negosyo Center",
                        "One Town, One Product (OTOP)",
                        "Pangkabuhayan para sa Pagbangon at Ginhawa (PPG)",
                        "Pondo sa Pagbabago at Pag-asenso (P3) / Other Financing Services through SB CORP",
                        "Regional Interactive Platform for Philippine Exporters (RIPPLES)",
                        "Rural Agro-enterprise Partnership for Inclusive Development (RAPID) Growth Project",
                        "Shared Service Facilities (SSF)",
                        "SME Roving Academy (SMERA)",
                        "Youth Entrepreneurship Program (YEP)",
                        "Zero to Hero"
                    ]
                    new_entry["MSME Program"] = st.selectbox(
                        "MSME Program *",
                        msme_program_options,
                        key=f"ast_msme_program_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">MSME Availed <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    msme_availed_date = st.date_input(
                        "MSME Availed *",
                        value=None,
                        key=f"ast_msme_availed_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                    new_entry["MSME Availed (MM/DD/YYYY)"] = msme_availed_date.strftime("%m/%d/%Y") if msme_availed_date else ""
                with col3:
                    st.markdown('<label style="color: black;">Assisted By <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    new_entry["Assisted By"] = st.text_input(
                        "Assisted By *",
                        key=f"ast_assisted_by_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 4: Assisting Office (Required), Type of NC (Optional), Location of NC (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Assisting Office <span style="color: red;">*</span></label>', unsafe_allow_html=True)
                    assisting_office_options = [
                        "",
                        "Technical Admin (ISMS)",
                        "Negosyo Center",
                        "Provincial Office Admin",
                        "Project Management Office",
                        "Regional Office Admin",
                        "Head Office"
                    ]
                    new_entry["Assisting Office"] = st.selectbox(
                        "Assisting Office *",
                        assisting_office_options,
                        key=f"ast_assisting_office_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Type of NC (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Type of NC"] = st.text_input(
                        "Type of NC",
                        key=f"ast_type_nc_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Location of NC (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Location of NC"] = st.text_input(
                        "Location of NC",
                        key=f"ast_location_nc_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Assisting Officer Location Information using create_location_widgets
                st.markdown("#### Assisting Officer Location Information")
                location_data = create_location_widgets()
                new_entry["Assisting Officer Region"] = location_data["region"]
                new_entry["Assisting Officer Province"] = location_data["province"]  
                new_entry["Assisting Officer City"] = location_data["city"]
                
                # Row 5: Jobs Generated (Optional), Investment Generated (Optional), Domestic Sales Generated (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Jobs Generated (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Jobs Generated"] = st.text_input(
                        "Jobs Generated",
                        key=f"ast_jobs_generated_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Investment Generated (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Investment Generated"] = st.text_input(
                        "Investment Generated",
                        key=f"ast_investment_generated_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Domestic Sales Generated (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Domestic Sales Generated"] = st.text_input(
                        "Domestic Sales Generated",
                        key=f"ast_domestic_sales_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 6: Export Sales Generated (Optional), Amount Loan Grant (Optional), Training Fund Source (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Export Sales Generated (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Export Sales Generated"] = st.text_input(
                        "Export Sales Generated",
                        key=f"ast_export_sales_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Amount Loan Grant (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Amount Loan Grant"] = st.text_input(
                        "Amount Loan Grant",
                        key=f"ast_loan_grant_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Training – Fund Source (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Training – Fund Source"] = st.text_input(
                        "Training – Fund Source",
                        key=f"ast_training_fund_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Training Demographics Section  
                st.markdown("#### Training Demographics (Optional)")
                
                # Row 7: Training Abled Male/Female, PWD Male/Female
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Training – Abled Male (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Training – Abled Male"] = st.text_input(
                        "Training – Abled Male",
                        key=f"ast_training_abled_m_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Training – Abled Female (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Training – Abled Female"] = st.text_input(
                        "Training – Abled Female",
                        key=f"ast_training_abled_f_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Training – PWD Male (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Training – PWD Male"] = st.text_input(
                        "Training – PWD Male",
                        key=f"ast_training_pwd_m_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 8: Training PWD Female, Indigenous Male/Female
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Training – PWD Female (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Training – PWD Female"] = st.text_input(
                        "Training – PWD Female",
                        key=f"ast_training_pwd_f_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Training – Indigenous Male (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Training – Indigenous Male"] = st.text_input(
                        "Training – Indigenous Male",
                        key=f"ast_training_ind_m_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Training – Indigenous Female (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Training – Indigenous Female"] = st.text_input(
                        "Training – Indigenous Female",
                        key=f"ast_training_ind_f_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 9: Training Senior Male/Female
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Training – Senior Male (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Training – Senior Male"] = st.text_input(
                        "Training – Senior Male",
                        key=f"ast_training_senior_m_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Training – Senior Female (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Training – Senior Female"] = st.text_input(
                        "Training – Senior Female",
                        key=f"ast_training_senior_f_{st.session_state.get('ast_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Validate required fields
                for field in required_fields:
                    if field in ["Assisting Officer Region", "Assisting Officer Province", "Assisting Officer City"]:
                        # For location fields, check the location_data
                        field_mapping = {
                            "Assisting Officer Region": "region",
                            "Assisting Officer Province": "province", 
                            "Assisting Officer City": "city"
                        }
                        if not location_data.get(field_mapping[field], "").strip():
                            validation_errors.append(field)
                    else:
                        if not new_entry.get(field, "").strip():
                            validation_errors.append(field)
                
                # Submit button
                submitted = st.button("Submit", key="ast_submit")
                
                if submitted:
                    if validation_errors:
                        st.error("Please fill in all required fields marked with *")
                        for field in validation_errors:
                            st.error(f"Missing: {field}")
                    else:
                        # Auto-increment 'No' and ensure order
                        data = st.session_state[table_key]
                        next_no = len(data) + 1
                        row = [str(next_no)]
                        for col in columns[1:]:
                            row.append(new_entry.get(col, ""))
                        data.append(row)
                        st.session_state[table_key] = data
                        save_current_data(selected)
                        
                        st.success("Assistance saved successfully!")
                        
                        # Clear form fields by incrementing counter
                        if 'ast_form_counter' not in st.session_state:
                            st.session_state.ast_form_counter = 0
                        st.session_state.ast_form_counter += 1
                        
                        # Close form
                        st.session_state[form_state_key] = False
                        st.rerun()
                        
            elif selected == "Jobs Generated":
                st.markdown(f"### Add Entry to {selected}")
                
                # All fields are optional (no required fields)
                validation_errors = []
                new_entry = {}
                
                # Row 1: Date Recorded (Optional), Direct Community Jobs (Optional), Indirect Community Jobs (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Date Recorded (Optional)</label>', unsafe_allow_html=True)
                    date_recorded = st.date_input(
                        "Date Recorded",
                        value=None,
                        key=f"jg_date_recorded_{st.session_state.get('jg_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                    new_entry["Date Recorded (MM/DD/YYYY)"] = date_recorded.strftime("%m/%d/%Y") if date_recorded else ""
                with col2:
                    st.markdown('<label style="color: black;">Direct Community Jobs (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Direct Community Jobs"] = st.text_input(
                        "Direct Community Jobs",
                        key=f"jg_direct_community_{st.session_state.get('jg_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Indirect Community Jobs (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Indirect Community Jobs"] = st.text_input(
                        "Indirect Community Jobs",
                        key=f"jg_indirect_community_{st.session_state.get('jg_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 2: Direct Home Based (Optional), Indirect Home Based (Optional), Direct Jobs Sustained (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Direct Home Based (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Direct Home Based"] = st.text_input(
                        "Direct Home Based",
                        key=f"jg_direct_home_{st.session_state.get('jg_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col2:
                    st.markdown('<label style="color: black;">Indirect Home Based (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Indirect Home Based"] = st.text_input(
                        "Indirect Home Based",
                        key=f"jg_indirect_home_{st.session_state.get('jg_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                with col3:
                    st.markdown('<label style="color: black;">Direct Jobs Sustained (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Direct Jobs Sustained"] = st.text_input(
                        "Direct Jobs Sustained",
                        key=f"jg_direct_sustained_{st.session_state.get('jg_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Row 3: Indirect Jobs Sustained (Optional)
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown('<label style="color: black;">Indirect Jobs Sustained (Optional)</label>', unsafe_allow_html=True)
                    new_entry["Indirect Jobs Sustained"] = st.text_input(
                        "Indirect Jobs Sustained",
                        key=f"jg_indirect_sustained_{st.session_state.get('jg_form_counter', 0)}",
                        label_visibility="collapsed"
                    )
                
                # Submit button (no validation needed since all fields are optional)
                submitted = st.button("Submit", key="jg_submit")
                
                if submitted:
                    # Auto-increment 'No' and ensure order
                    data = st.session_state[table_key]
                    next_no = len(data) + 1
                    row = [str(next_no)]
                    for col in columns[1:]:
                        row.append(new_entry.get(col, ""))
                    data.append(row)
                    st.session_state[table_key] = data
                    save_current_data(selected)
                    
                    st.success("Jobs Generated saved successfully!")
                    
                    # Clear form fields by incrementing counter
                    if 'jg_form_counter' not in st.session_state:
                        st.session_state.jg_form_counter = 0
                    st.session_state.jg_form_counter += 1
                    
                    # Close form
                    st.session_state[form_state_key] = False
                    st.rerun()

        # Refresh data after any form submissions - Create DataFrame from updated session state
        data = st.session_state[table_key]
        columns = st.session_state[col_key]
        
        # Convert to DataFrame for editing
        df = pd.DataFrame(data, columns=columns)
        
        # Build column config with appropriate types
        column_config = {}
        for col in df.columns:
            if col == "No":
                # Handle row number column
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                    df[col] = range(1, len(df) + 1)  # Ensure sequential numbering
                except:
                    df[col] = range(1, len(df) + 1)
                column_config[col] = st.column_config.NumberColumn(
                    label=col, 
                    required=True,
                    disabled=True  # Don't allow editing the row number
                )
            else:
                # Convert all other columns to text to avoid type conflicts
                df[col] = df[col].astype(str).replace('nan', '')
                column_config[col] = st.column_config.TextColumn(
                    label=col,
                    required=True if col.endswith("*") else False
                )

        # Display current data summary in sidebar
        if len(df) > 0:
            st.sidebar.markdown(f"**Total Entries:** {len(df)}")
            st.sidebar.markdown(f"**Columns:** {len(df.columns)}")
            
        # Data export section
        if len(df) > 0:
            csv = df.to_csv(index=False)
            st.sidebar.download_button(
                label=f"Download {selected} as CSV",
                data=csv,
                file_name=f"{selected.lower().replace(' ', '_')}_data.csv",
                mime="text/csv"
            )

        # After all form logic, always show the table for the selected sheet

        # Display the data table
        st.markdown("### Current Data")
        
        # Show the data editor for the selected sheet
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            column_config=column_config,
            hide_index=True,
            width=None,
            height=400
        )
        
        # Save data whenever it changes
        if not edited_df.equals(df):
            st.session_state[table_key] = edited_df.values.tolist()
            save_current_data(selected)

        # Delete functionality buttons
        st.markdown("### Data Management")
        
        # Initialize undo data storage if not exists
        undo_key = f"undo_data_{selected}"
        if undo_key not in st.session_state:
            st.session_state[undo_key] = []
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Delete Row", key=f"delete_row_btn_{selected}", type="secondary", use_container_width=True):
                if len(df) > 0:
                    # Store current data for undo functionality
                    st.session_state[undo_key] = df.copy()
                    st.session_state.show_delete_row_input = True
                else:
                    st.warning("No data to delete!")
        
        with col2:
            if st.button("Delete All Rows", key=f"delete_all_btn_{selected}", type="secondary", use_container_width=True):
                if len(df) > 0:
                    # Store current data for undo functionality
                    st.session_state[undo_key] = df.copy()
                    # Clear all data
                    st.session_state[table_key] = []
                    save_current_data(selected)
                    st.success("All rows deleted successfully!")
                    st.rerun()
                else:
                    st.warning("No data to delete!")
        
        with col3:
            if st.button("Undo", key=f"undo_btn_{selected}", type="primary", use_container_width=True):
                if undo_key in st.session_state and len(st.session_state[undo_key]) > 0:
                    # Restore data from undo storage
                    restored_df = st.session_state[undo_key]
                    st.session_state[table_key] = restored_df.values.tolist()
                    save_current_data(selected)
                    # Clear undo data after use
                    st.session_state[undo_key] = []
                    st.success("Data restored successfully!")
                    st.rerun()
                else:
                    st.warning("No previous action to undo!")
        
        # Show row deletion input if delete row button was clicked
        if st.session_state.get('show_delete_row_input', False):
            st.markdown("#### Delete Specific Row")
            if len(df) > 0:
                row_options = [f"Row {i+1}" for i in range(len(df))]
                selected_row = st.selectbox(
                    "Select row to delete:",
                    options=row_options,
                    key=f"delete_row_select_{selected}"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Confirm Delete", key=f"confirm_delete_{selected}", type="secondary"):
                        if selected_row:
                            row_index = int(selected_row.split(" ")[1]) - 1  # Extract row number and convert to 0-based index
                            
                            # Remove the selected row
                            current_data = st.session_state[table_key]
                            if 0 <= row_index < len(current_data):
                                current_data.pop(row_index)
                                
                                # Renumber the remaining rows
                                for i, row in enumerate(current_data):
                                    row[0] = str(i + 1)  # Update the "No" column
                                
                                st.session_state[table_key] = current_data
                                save_current_data(selected)
                                st.session_state.show_delete_row_input = False
                                st.success(f"{selected_row} deleted successfully!")
                                st.rerun()
                
                with col2:
                    if st.button("Cancel", key=f"cancel_delete_{selected}", type="primary"):
                        st.session_state.show_delete_row_input = False
                        st.rerun()
            else:
                st.warning("No rows available to delete!")
                st.session_state.show_delete_row_input = False

    # Close main content wrapper and end of show() function
    st.markdown('</div>', unsafe_allow_html=True)
