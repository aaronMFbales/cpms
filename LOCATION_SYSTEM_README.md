# Philippine Hierarchical Location System

## Overview

This system implements a comprehensive hierarchical location selection for the Philippines with cascading dropdowns that follow the administrative structure: **Region → Province → City/Municipality → Barangay → Purok**.

## Features

### 🎯 Hierarchical Selection
- **Cascading Dropdowns**: Each selection filters the next level
- **Region Selection**: Choose from all 17 Philippine regions
- **Province Selection**: Only shows provinces relevant to the selected region
- **City/Municipality Selection**: Only shows cities relevant to the selected province
- **Barangay Selection**: Only shows barangays relevant to the selected city
- **Purok Selection**: Only shows puroks relevant to the selected barangay

### 📍 Comprehensive Coverage
- **17 Regions**: All Philippine administrative regions including NCR, CAR, BARMM, and numbered regions
- **Complete Hierarchy**: Full 5-level administrative structure
- **Real Locations**: Based on actual Philippine administrative divisions

### 🔧 Easy Integration
- **Utility Functions**: Simple functions to get location data
- **Widget Creation**: Ready-to-use Streamlit widgets
- **Form Integration**: Seamlessly integrated into existing forms

## Implementation

### File Structure
```
utils/
└── philippine_locations.py    # Main location utility
modules/
├── dashboard.py               # Updated with location widgets
└── login.py                  # Updated imports
pages/
└── signup.py                 # Updated with location fields
```

### Key Functions

#### `create_location_widgets()`
Creates cascading location selection widgets for Streamlit forms.

**Returns:**
```python
{
    "region": "Selected Region",
    "province": "Selected Province", 
    "city": "Selected City",
    "barangay": "Selected Barangay",
    "purok": "Selected Purok"
}
```

#### Individual Getter Functions
- `get_regions()` - Returns list of all regions
- `get_provinces(region)` - Returns provinces for a region
- `get_cities(region, province)` - Returns cities for a province
- `get_barangays(region, province, city)` - Returns barangays for a city
- `get_puroks(region, province, city, barangay)` - Returns puroks for a barangay

## Usage Examples

### 1. Basic Form Integration
```python
from utils.philippine_locations import create_location_widgets

# In your Streamlit form
location_data = create_location_widgets()

# Access the selected values
region = location_data["region"]
province = location_data["province"]
city = location_data["city"]
barangay = location_data["barangay"]
purok = location_data["purok"]
```

### 2. Individual Location Queries
```python
from utils.philippine_locations import get_provinces, get_cities

# Get provinces for a specific region
provinces = get_provinces("Region 4-A CALABARZON")

# Get cities for a specific province
cities = get_cities("Region 4-A CALABARZON", "Laguna")
```

### 3. Form Integration in Dashboard
The location system is now integrated into:
- **Business Contact Information** form
- **Business Owner** form  
- **Assistance** form (for assisting officer location)
- **Signup** form (for user registration)

## Data Structure

The location data is stored in a nested dictionary structure:

```python
PHILIPPINE_LOCATIONS = {
    "Region Name": {
        "Province Name": {
            "City Name": {
                "Barangay Name": ["Purok 1", "Purok 2", "Purok 3"]
            }
        }
    }
}
```

## Regions Covered

1. **National Capital Region (NCR)**
2. **Cordillera Administrative Region (CAR)**
3. **Region 1 (Ilocos Region)**
4. **Region 2 (Cagayan Valley)**
5. **Region 3 (Central Luzon)**
6. **Region 4-A CALABARZON**
7. **MIMAROPA**
8. **Region 5 (Bicol Region)**
9. **Region 6 (Western Visayas)**
10. **Region 7 (Central Visayas)**
11. **Region 8 (Eastern Visayas)**
12. **Region 9 (Zamboanga Peninsula)**
13. **Region 10 (Northern Mindanao)**
14. **Region 11 (Davao Region)**
15. **Region 12 (SOCCSKSARGEN)**
16. **Region 13 CARAGA**
17. **BARMM**

## Form Updates

### Business Contact Information
- ✅ Updated with hierarchical location selection
- ✅ Includes Region, Province, City/Municipality, Barangay, Purok
- ✅ Maintains existing fields (District, Address, etc.)

### Business Owner
- ✅ Updated with hierarchical location selection
- ✅ Includes complete location hierarchy
- ✅ Maintains personal information fields

### Assistance Form
- ✅ Updated assisting officer location selection
- ✅ Includes full location hierarchy for officer
- ✅ Maintains all assistance-related fields

### Signup Form
- ✅ Added location information section
- ✅ Includes complete location hierarchy
- ✅ Location data saved with user registration
- ✅ Location included in admin notification emails

## Benefits

### 🎯 User Experience
- **Intuitive Navigation**: Users can easily find their location
- **Reduced Errors**: Cascading dropdowns prevent invalid combinations
- **Faster Data Entry**: No need to type location names
- **Consistent Data**: Standardized location names and structure

### 📊 Data Quality
- **Structured Data**: Consistent location hierarchy
- **Searchable**: Easy to filter and search by location
- **Analytics Ready**: Hierarchical data supports geographic analysis
- **Validation**: Built-in validation prevents invalid location combinations

### 🔧 Technical Benefits
- **Maintainable**: Centralized location data
- **Extensible**: Easy to add new locations
- **Reusable**: Location widgets can be used in any form
- **Performance**: Efficient data structure for lookups

## Testing

Run the test script to verify the system works correctly:

```bash
python test_location_system.py
```

This will test:
- ✅ All getter functions
- ✅ Invalid location combinations
- ✅ Data structure integrity
- ✅ Hierarchical relationships

## Future Enhancements

### Potential Improvements
1. **More Detailed Data**: Add more barangays and puroks for each city
2. **Postal Codes**: Include postal code information
3. **GPS Coordinates**: Add latitude/longitude data
4. **Map Integration**: Visual map selection
5. **Search Functionality**: Text search for locations
6. **Import/Export**: CSV/Excel import/export of location data

### Data Sources
- Philippine Statistics Authority (PSA)
- Department of Interior and Local Government (DILG)
- Local Government Units (LGUs)

## Support

For questions or issues with the location system:
1. Check the test script output
2. Verify the location data structure
3. Ensure proper imports in your modules
4. Test with the provided examples

---

**Note**: This system provides a comprehensive foundation for Philippine location selection. The data can be expanded with more detailed information as needed for specific use cases. 