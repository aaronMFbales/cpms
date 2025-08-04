"""
Philippine Location Data Utility
Contains hierarchical location data for the Philippines: Region → Province → City/Municipality → Barangay → Purok
"""

import streamlit as st
import pandas as pd
import os

def load_location_data():
    """Load Philippine location data from CSV files"""
    data_dir = "data"
    
    # Load CSV files
    regions_df = pd.read_csv(os.path.join(data_dir, "refregion.csv"))
    provinces_df = pd.read_csv(os.path.join(data_dir, "refprovince.csv"))
    cities_df = pd.read_csv(os.path.join(data_dir, "refcitymun.csv"))
    barangays_df = pd.read_csv(os.path.join(data_dir, "refbrgy.csv"))
    
    return regions_df, provinces_df, cities_df, barangays_df

def create_location_widgets():
    """Create simple cascading dropdown widgets without forms"""
    
    # Load data
    regions_df, provinces_df, cities_df, barangays_df = load_location_data()
    
    # Initialize session state for location selections
    if 'loc_region' not in st.session_state:
        st.session_state.loc_region = None
    if 'loc_province' not in st.session_state:
        st.session_state.loc_province = None
    if 'loc_city' not in st.session_state:
        st.session_state.loc_city = None
    if 'loc_barangay' not in st.session_state:
        st.session_state.loc_barangay = None
    
    # Create 4 columns for each location level
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("### Region")
        regions = regions_df['regDesc'].unique()
        selected_region = st.selectbox("Select Region:", regions, key="loc_region_select")
        
        # Update session state when region changes
        if selected_region != st.session_state.loc_region:
            st.session_state.loc_region = selected_region
            st.session_state.loc_province = None
            st.session_state.loc_city = None
            st.session_state.loc_barangay = None
            st.rerun()
    
    with col2:
        st.markdown("### Province")
        if st.session_state.loc_region:
            region_code = regions_df[regions_df['regDesc'] == st.session_state.loc_region]['regCode'].iloc[0]
            provinces = provinces_df[provinces_df['regCode'] == region_code]['provDesc'].unique()
            selected_province = st.selectbox("Select Province:", provinces, key="loc_province_select")
            
            # Update session state when province changes
            if selected_province != st.session_state.loc_province:
                st.session_state.loc_province = selected_province
                st.session_state.loc_city = None
                st.session_state.loc_barangay = None
                st.rerun()
        else:
            selected_province = st.selectbox("Select Province:", ["Select Region First"], key="loc_province_select")
    
    with col3:
        st.markdown("### City/Municipality")
        if st.session_state.loc_province:
            province_code = provinces_df[provinces_df['provDesc'] == st.session_state.loc_province]['provCode'].iloc[0]
            cities = cities_df[cities_df['provCode'] == province_code]['citymunDesc'].unique()
            selected_city = st.selectbox("Select City:", cities, key="loc_city_select")
            
            # Update session state when city changes
            if selected_city != st.session_state.loc_city:
                st.session_state.loc_city = selected_city
                st.session_state.loc_barangay = None
                st.rerun()
        else:
            selected_city = st.selectbox("Select City:", ["Select Province First"], key="loc_city_select")
    
    with col4:
        st.markdown("### Barangay")
        if st.session_state.loc_city:
            city_code = cities_df[cities_df['citymunDesc'] == st.session_state.loc_city]['citymunCode'].iloc[0]
            barangays = barangays_df[barangays_df['citymunCode'] == city_code]['brgyDesc'].unique()
            selected_barangay = st.selectbox("Select Barangay:", barangays, key="loc_barangay_select")
            
            # Update session state when barangay changes
            if selected_barangay != st.session_state.loc_barangay:
                st.session_state.loc_barangay = selected_barangay
        else:
            selected_barangay = st.selectbox("Select Barangay:", ["Select City First"], key="loc_barangay_select")
    
    # Return selected location data
    return {
        "region": st.session_state.loc_region or selected_region,
        "province": st.session_state.loc_province or selected_province,
        "city": st.session_state.loc_city or selected_city,
        "barangay": st.session_state.loc_barangay or selected_barangay,
        "purok": "N/A"  # Purok data not available in standard PSGC
    } 