"""
PSIC (Philippine Standard Industrial Classification) Handler
Loads and provides cascading dropdown functionality for PSIC data from Excel file
"""

import pandas as pd
import streamlit as st
import os

@st.cache_data
def load_psic_data():
    """Load and organize PSIC data from Excel file"""
    file_path = "data/2019_Updates_to_the_2009_PSIC_08112021.xlsx"
    
    psic_hierarchy = {
        'sections': {},  # Section code -> description
        'divisions': {},  # Division code -> {'description': str, 'section': section_code}
        'groups': {},    # Group code -> {'description': str, 'division': division_code}
        'section_divisions': {},  # Section -> List of divisions
        'division_groups': {}     # Division -> List of groups
    }
    
    if not os.path.exists(file_path):
        return psic_hierarchy
    
    try:
        xl_file = pd.ExcelFile(file_path)
        current_section = ""
        current_division = ""
        
        for sheet_name in xl_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            
            for i in range(len(df)):
                row_data = df.iloc[i].dropna().tolist()
                if not row_data:
                    continue
                    
                text = str(row_data[0])
                
                # Check for SECTION
                if 'SECTION' in text and '.' in text:
                    section_parts = text.split('.')
                    section_code = section_parts[0].replace('SECTION ', '').strip()
                    section_desc = section_parts[1].strip()
                    
                    current_section = section_code
                    psic_hierarchy['sections'][section_code] = section_desc
                    psic_hierarchy['section_divisions'][section_code] = []
                
                # Check for DIVISION  
                elif 'DIVISION' in text and '.' in text and current_section:
                    div_parts = text.split('.')
                    div_code = div_parts[0].replace('DIVISION ', '').strip()
                    div_desc = div_parts[1].strip()
                    
                    current_division = div_code
                    psic_hierarchy['divisions'][div_code] = {
                        'description': div_desc,
                        'section': current_section
                    }
                    psic_hierarchy['section_divisions'][current_section].append(div_code)
                    psic_hierarchy['division_groups'][div_code] = []
                
                # Check for GROUP (3-digit codes)
                elif len(row_data) >= 2 and current_division:
                    try:
                        if isinstance(row_data[0], (int, float)):
                            group_code = str(int(row_data[0]))
                            if len(group_code) == 3:
                                group_desc = str(row_data[1]) if len(row_data) > 1 else ''
                                
                                psic_hierarchy['groups'][group_code] = {
                                    'description': group_desc,
                                    'division': current_division
                                }
                                psic_hierarchy['division_groups'][current_division].append(group_code)
                    except:
                        continue
        
        xl_file.close()
        
    except Exception as e:
        print(f"Error loading PSIC data: {e}")
    
    return psic_hierarchy

def create_psic_widgets():
    """Create cascading PSIC dropdowns"""
    
    # Load PSIC data
    psic_data = load_psic_data()
    
    # Initialize session state for PSIC selections
    if 'psic_section' not in st.session_state:
        st.session_state.psic_section = ""
    if 'psic_division' not in st.session_state:
        st.session_state.psic_division = ""
    if 'psic_group' not in st.session_state:
        st.session_state.psic_group = ""
    
    # Create 3 columns for PSIC fields
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # PSIC Section dropdown
        st.markdown('<label style="color: black;">PSIC Section <span style="color: red;">*</span></label>', unsafe_allow_html=True)
        
        section_options = [""] + [f"{code} - {desc}" for code, desc in psic_data['sections'].items()]
        selected_section_display = st.selectbox(
            "PSIC Section *",
            section_options,
            key="psic_section_select",
            label_visibility="collapsed"
        )
        
        # Extract section code
        selected_section = ""
        if selected_section_display and selected_section_display != "":
            selected_section = selected_section_display.split(" - ")[0]
        
        # Update session state when section changes
        if selected_section != st.session_state.psic_section:
            st.session_state.psic_section = selected_section
            st.session_state.psic_division = ""
            st.session_state.psic_group = ""
            st.rerun()
    
    with col2:
        # PSIC Division dropdown
        st.markdown('<label style="color: black;">PSIC Division <span style="color: red;">*</span></label>', unsafe_allow_html=True)
        
        if st.session_state.psic_section and st.session_state.psic_section in psic_data['section_divisions']:
            division_codes = psic_data['section_divisions'][st.session_state.psic_section]
            division_options = [""] + [
                f"{code} - {psic_data['divisions'][code]['description']}" 
                for code in division_codes 
                if code in psic_data['divisions']
            ]
            
            selected_division_display = st.selectbox(
                "PSIC Division *",
                division_options,
                key="psic_division_select",
                label_visibility="collapsed"
            )
            
            # Extract division code
            selected_division = ""
            if selected_division_display and selected_division_display != "":
                selected_division = selected_division_display.split(" - ")[0]
            
            # Update session state when division changes
            if selected_division != st.session_state.psic_division:
                st.session_state.psic_division = selected_division
                st.session_state.psic_group = ""
                st.rerun()
        else:
            selected_division_display = st.selectbox(
                "PSIC Division *",
                ["Select Section First"],
                key="psic_division_select",
                label_visibility="collapsed"
            )
    
    with col3:
        # PSIC Group dropdown
        st.markdown('<label style="color: black;">PSIC Group <span style="color: red;">*</span></label>', unsafe_allow_html=True)
        
        if st.session_state.psic_division and st.session_state.psic_division in psic_data['division_groups']:
            group_codes = psic_data['division_groups'][st.session_state.psic_division]
            group_options = [""] + [
                f"{code} - {psic_data['groups'][code]['description']}" 
                for code in group_codes 
                if code in psic_data['groups']
            ]
            
            selected_group_display = st.selectbox(
                "PSIC Group *",
                group_options,
                key="psic_group_select",
                label_visibility="collapsed"
            )
            
            # Extract group code
            selected_group = ""
            if selected_group_display and selected_group_display != "":
                selected_group = selected_group_display.split(" - ")[0]
            
            # Update session state when group changes
            if selected_group != st.session_state.psic_group:
                st.session_state.psic_group = selected_group
        else:
            selected_group_display = st.selectbox(
                "PSIC Group *",
                ["Select Division First"],
                key="psic_group_select",
                label_visibility="collapsed"
            )
    
    # Return selected PSIC data (just the codes for storage)
    return {
        "section": st.session_state.psic_section,
        "division": st.session_state.psic_division, 
        "group": st.session_state.psic_group,
        "section_desc": psic_data['sections'].get(st.session_state.psic_section, ""),
        "division_desc": psic_data['divisions'].get(st.session_state.psic_division, {}).get('description', ""),
        "group_desc": psic_data['groups'].get(st.session_state.psic_group, {}).get('description', "")
    }
