import pandas as pd


# #### Outpatient Survey

outpatient = pd.read_csv('Outpatient.csv')
columns_t_drop = list(range(6, 11)) + [2] + list(range(12, 15)) + list(range(16, 19)) + list(range(20, 23)) + list(range(24, 26)) + [28, 29]
outpatient.drop(outpatient.columns[columns_t_drop], axis = 1, inplace=True)


columns_with_linear_score = outpatient.columns[outpatient.columns.str.contains('linear mean score', case=False)]
outpatient = outpatient.dropna(subset=columns_with_linear_score)

outpatient = outpatient[(outpatient['State'] == 'IL')]



# #### Nursing Home Survey


Nursing = pd.read_csv('Nursing_Home.csv')

Nursing = Nursing[(Nursing['County/Parish'] == 'Cook') & (Nursing['State'] == 'IL')]

columns_to_drop = list(range(6, 8)) + [2] + list(range(9, 26)) + list(range(38, 96))
Nursing.drop(Nursing.columns[columns_to_drop], axis = 1, inplace=True)

columns_with_footnote = Nursing.columns[Nursing.columns.str.contains('footnote', case=False)]
Nursing = Nursing.drop(columns=columns_with_footnote)

Nursing = Nursing.drop(columns= 'Processing Date')

Nursing.to_csv('cleaned_file_Nursing_demo.csv', index=False)


# #### Homecare Survey

Homecare = pd.read_csv('Home_care.csv')

#CMS code for IL starts with 78, 14
Homecare = Homecare[Homecare['CMS Certification Number (CCN)'].astype(str).str.startswith('78') | Homecare['CMS Certification Number (CCN)'].astype(str).str.startswith('14')]
Homecare.shape


Homecare = Homecare[Homecare['HHCAHPS Survey Summary Star Rating'] != 'Not Available']
columns_footnote = Homecare.columns[Homecare.columns.str.contains('footnote', case=False)]
Homecare = Homecare.drop(columns=columns_footnote)
Homecare = Homecare.drop(columns=['Survey response rate'])

columns_percent = Homecare.columns[Homecare.columns.str.contains('percent', case=False)]
Homecare = Homecare.drop(columns=columns_percent)

Homecare.to_csv('C:/Users/Hourui Kaku/Documents/CS2/Final Project/CAHPS standard surveys/Cleaned_surveys/clean_homecare.csv', index=False)


# #### Inpatient survey


Inpatient = pd.read_csv('Inpatient.csv')


Inpatient = Inpatient[(Inpatient['County/Parish'] == 'COOK') & (Inpatient['State'] == 'IL')]
columns_drop = list(range(7, 10)) + [13,18,20,21]
Inpatient.drop(Inpatient.columns[columns_drop], axis = 1, inplace=True)

columns_w_footnote = Inpatient.columns[Inpatient.columns.str.contains('footnote', case=False)]
Inpatient = Inpatient.drop(columns=columns_w_footnote)
Inpatient = Inpatient.drop(columns= ['Address'])

Inpatient = Inpatient[Inpatient['HCAHPS Answer Description'].str.contains('linear mean score|star rating', case=False, na=False)]


Inpatient.rename(columns={'Facility ID': 'CMS Certification Number (CCN)'}, inplace=True)

Inpatient = Inpatient[Inpatient['Patient Survey Star Rating'] != 'Not Applicable']
Inpatient.drop('HCAHPS Linear Mean Value', axis=1, inplace=True)


# List of all possible HCAHPS Answer Descriptions
all_descriptions = [
    'Nurse communication - star rating', 'Doctor communication - star rating',
    'Staff responsiveness - star rating', 'Communication about medicines - star rating',
    'Discharge information - star rating', 'Care transition - star rating',
    'Cleanliness - star rating', 'Quietness - star rating',
    'Overall hospital rating - star rating', 'Recommend hospital - star rating',
    'Summary star rating'
]

# Create the pivot table
pivoted_df = Inpatient.pivot_table(
    index=['CMS Certification Number (CCN)', 'Facility Name', 'City/Town', 'State', 'ZIP Code', 'County/Parish', 'Number of Completed Surveys'],
    columns='HCAHPS Answer Description',
    values='Patient Survey Star Rating',
    aggfunc='first',
    fill_value='NA'
)

# Reindex with all possible descriptions
pivoted_df = pivoted_df.reindex(all_descriptions, axis=1, fill_value='NA')

# Flatten the column index if necessary
pivoted_df.columns = [col for col in pivoted_df.columns]

# Reset index to make 'CMS Certification Number (CCN)' a column again
pivoted_df.reset_index(inplace=True)

# Save to a new CSV
pivoted_df.to_csv('C:/Users/Hourui Kaku/Documents/CS2/Final Project/CAHPS standard surveys/Cleaned_surveys/clean_inpatient.csv', index=False)


# #### Maping Demo for possible mapping in the future

pip install geopandas folium


import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
import numpy as np
import math


geodf = gpd.read_file('cleaned_file_Nursing_demo.csv')

#Change the column data type to float
geodf['Latitude'] = geodf['Latitude'].astype(float)
geodf['Longitude'] = geodf['Longitude'].astype(float)


# Create a Folium map centered on a general point in Cook County
cook_county_map = folium.Map(location=[41.7377, -87.6976], zoom_start=10)

# Create a MarkerCluster for better visualization
marker_cluster = MarkerCluster().add_to(cook_county_map)

# Iterate through the GeoDataFrame to create markers for each nursing home
for idx, row in geodf.iterrows():
    # Only add markers if there's a valid overall rating
    if pd.notna(row['Overall Rating']):
        folium.Marker(
            location=(row['Latitude'], row['Longitude']),
            popup=(
                f"Name: {row['Provider Name']}<br>"
                f"Overall Rating: {row['Overall Rating']}<br>"
                f"QM Rating: {row['QM Rating']}<br>"
                f"Health Inspection Rating: {row['Health Inspection Rating']}<br>"
                f"Staffing Rating: {row['Staffing Rating']}"
            ),
            icon=folium.Icon(color='green' if row['Overall Rating'] in ['4', '5'] else 'orange' if row['Overall Rating'] == '3' else 'red')
        ).add_to(marker_cluster)

# Save the map as an HTML file
output_filepath = 'C:/Users/Hourui Kaku/Documents/CS2/Final Project/CAHPS standard surveys/cook_county_nursing_homes_map.html'
cook_county_map.save(output_filepath)
output_filepath


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in miles between two points 
    on the earth(Refer to PA3)
    """
    # Radius of Earth in miles
    EARTH_R_MI = 3963
    
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Haversine formula part
    delta_lat = lat2_rad - lat1_rad
    delta_lon = lon2_rad - lon1_rad
    a = math.sin(delta_lat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    distance = EARTH_R_MI * c
    return distance
    

# Let's redefine the filter function using the Haversine formula
def filter_nursing_homes_haversine(df, lat, lon, radius=5):
    # Calculate the distance for each row using the Haversine formula
    df['Distance'] = df.apply(lambda row: haversine(lon, lat, row['Longitude'], row['Latitude']), axis=1)
    # Filter rows for the given radius and sort by 'Overall Rating'
    nearby_homes = df[df['Distance'] <= radius].sort_values('Overall Rating', ascending=False)
    return nearby_homes


# Use the function with the example latitude and longitude again
nearby_nursing_homes_haversine = filter_nursing_homes_haversine(geodf, 41.7961840, -87.5802810)

# Display the top 5 results
nearby_nursing_homes_haversine[['Provider Name', 'City/Town', 'ZIP Code', 'Overall Rating', 'Distance']].head()

def generate_map(df, lat, lon, radius=2):
    # Filter the DataFrame for nearby nursing homes using the haversine formula
    nearby_homes = filter_nursing_homes_haversine(df, lat, lon, radius)
    
    # Create a map centered at the input coordinates
    folium_map = folium.Map(location=[lat, lon], zoom_start=12)

    # Convert 'Overall Rating' to a numeric type, coerce errors to NaN
    df['Overall Rating'] = pd.to_numeric(df['Overall Rating'], errors='coerce')
    
    # Add markers for nearby nursing homes to the map
    for idx, row in nearby_homes.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=(
                f"Name: {row['Provider Name']}<br>"
                f"Overall Rating: {row['Overall Rating']}<br>"
                f"Distance: {row['Distance']:.2f} miles"
            ),
            tooltip=row['Provider Name'],
            icon=folium.Icon(
                color='green' if row['Overall Rating'] >= 4 else 'orange' if row['Overall Rating'] == 3 else 'red'
            )
        ).add_to(folium_map)

    return folium_map

generate_map(geodf, 41.8781, -87.6298, 2).save('C:/Users/Hourui Kaku/Documents/CS2/Final Project/CAHPS standard surveys/Map_demo/example_map.html')
