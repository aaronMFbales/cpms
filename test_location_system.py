#!/usr/bin/env python3
"""
Test script for the Philippine Location System
"""

from utils.philippine_locations import (
    get_regions, 
    get_provinces, 
    get_cities, 
    get_barangays, 
    get_puroks,
    PHILIPPINE_LOCATIONS
)

def test_location_hierarchy():
    """Test the hierarchical location system"""
    print("Testing Philippine Location System")
    print("=" * 50)
    
    # Test 1: Get all regions
    regions = get_regions()
    print(f"Total regions: {len(regions)}")
    print(f"First 3 regions: {regions[:3]}")
    print()
    
    # Test 2: Get provinces for a specific region
    test_region = "Region 4-A CALABARZON"
    provinces = get_provinces(test_region)
    print(f"Provinces in {test_region}: {provinces}")
    print()
    
    # Test 3: Get cities for a specific province
    test_province = "Laguna"
    cities = get_cities(test_region, test_province)
    print(f"Cities in {test_province}, {test_region}: {cities}")
    print()
    
    # Test 4: Get barangays for a specific city
    test_city = "San Pablo City"
    barangays = get_barangays(test_region, test_province, test_city)
    print(f"Barangays in {test_city}, {test_province}, {test_region}: {barangays}")
    print()
    
    # Test 5: Get puroks for a specific barangay
    test_barangay = "Barangay 1"
    puroks = get_puroks(test_region, test_province, test_city, test_barangay)
    print(f"Puroks in {test_barangay}, {test_city}, {test_province}, {test_region}: {puroks}")
    print()
    
    # Test 6: Test invalid combinations
    print("Testing invalid combinations:")
    invalid_provinces = get_provinces("Invalid Region")
    print(f"Invalid region provinces: {invalid_provinces}")
    
    invalid_cities = get_cities("Invalid Region", "Invalid Province")
    print(f"Invalid region/province cities: {invalid_cities}")
    
    invalid_barangays = get_barangays("Invalid Region", "Invalid Province", "Invalid City")
    print(f"Invalid location barangays: {invalid_barangays}")
    
    invalid_puroks = get_puroks("Invalid Region", "Invalid Province", "Invalid City", "Invalid Barangay")
    print(f"Invalid location puroks: {invalid_puroks}")
    print()
    
    # Test 7: Show sample data structure
    print("Sample data structure:")
    sample_region = list(PHILIPPINE_LOCATIONS.keys())[0]
    sample_province = list(PHILIPPINE_LOCATIONS[sample_region].keys())[0]
    sample_city = list(PHILIPPINE_LOCATIONS[sample_region][sample_province].keys())[0]
    sample_barangay = list(PHILIPPINE_LOCATIONS[sample_region][sample_province][sample_city].keys())[0]
    
    print(f"Sample hierarchy:")
    print(f"  Region: {sample_region}")
    print(f"  Province: {sample_province}")
    print(f"  City: {sample_city}")
    print(f"  Barangay: {sample_barangay}")
    print(f"  Puroks: {PHILIPPINE_LOCATIONS[sample_region][sample_province][sample_city][sample_barangay]}")
    
    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    test_location_hierarchy() 