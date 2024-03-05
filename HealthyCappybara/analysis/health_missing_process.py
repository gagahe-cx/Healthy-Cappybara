## Written by Qi Zhao ##

# # Health Missing Data processing
import re
import pandas as pd
import geopandas as gpd


# define a function import data from doctor number and rating csv file
def save_doctors_stats_from_csv(csv_file_path, output_csv_file_path):
    df = pd.read_csv(csv_file_path)

    # create a new DataFrame to store the processed data
    processed_data = {"zipcode": [], "rating_score": []}

    for _, row in df.iterrows():
        try:
            zips = eval(row["zipcode"])
            if not isinstance(zips, list):
                zips = [zips]
        except:
            zips = [row["zipcode"]]

        # select zip codes that start with 6
        for zip_code in zips:
            if str(zip_code).startswith("6"):
                processed_data["zipcode"].append(zip_code)
                processed_data["rating_score"].append(row["rating_score"])

    # create a new DataFrame from the processed data
    new_df = pd.DataFrame(processed_data)
    new_df["rating_score"] = pd.to_numeric(new_df["rating_score"], errors="coerce")

    # group the data by zip code and calculate the number of doctors and the average rating
    grouped_df = (
        new_df.groupby("zipcode")
        .agg(num_doctors=("zipcode", "size"), average_rating=("rating_score", "mean"))
        .reset_index()
    )

    # save the grouped data to a new CSV file
    grouped_df.to_csv(output_csv_file_path, index=False)
    print(f"Data successfully saved to {output_csv_file_path}")


# define a function to update health data with neighbors
def update_health_data_with_neighbors(gdf, health_data, zip_code_column, data_columns):
    # Precompute the 'neighbors' column for all ZIP codes in gdf
    if "neighbors" not in gdf.columns:
        gdf["neighbors"] = gdf.geometry.apply(
            lambda geom: gdf[gdf.geometry.touches(geom)]["ZCTA5CE20"].tolist()
        )

    # Create a dictionary of neighbors only for the ZIP codes present in health_data
    zip_codes_in_health_data = health_data[zip_code_column].unique()
    neighbors_dict = (
        gdf[gdf["ZCTA5CE20"].isin(zip_codes_in_health_data)]
        .set_index("ZCTA5CE20")["neighbors"]
        .to_dict()
    )

    # Update health_data using the precomputed neighbors
    for index, row in health_data.iterrows():
        current_zip = row[zip_code_column]
        neighbors = neighbors_dict.get(current_zip, [])

        # Accumulate neighbor values for each column of interest
        for column in data_columns:
            neighbor_values = sum(
                health_data.loc[health_data[zip_code_column].isin(neighbors), column]
            )
            health_data.at[index, column] += neighbor_values

    return health_data


# combine web scraped data and health data
csv_file_path = r"C:\Users\ZhaoQ\Desktop\cappybara\raw data\combined_data.csv"
output_csv_file_path = r"C:\Users\ZhaoQ\Desktop\cappybara\raw data\doctors_zip.csv"
save_doctors_stats_from_csv(csv_file_path, output_csv_file_path)

## combine data from different sources
expense = pd.read_csv(r"C:\Users\ZhaoQ\Desktop\cappybara\health_expen.csv")
columns_to_keep = [
    "Zip Code",
    "hospital beds",
    "hospital cost per day",
    "nurse beds",
    "nurse cost per day",
    "home cost per visit",
]
expense = expense[columns_to_keep]
expense.fillna(0, inplace=True)
rate_inpatient = pd.read_csv(
    r"C:\Users\ZhaoQ\Desktop\cappybara\rating data\rate_inpatient.csv"
)
rate_inpatient = (
    rate_inpatient.groupby("ZIP Code")["Summary star rating"].mean().reset_index()
)

rate_nursing = pd.read_csv(
    r"C:\Users\ZhaoQ\Desktop\cappybara\rating data\rate_nursing.csv"
)
rate_nursing = rate_nursing.groupby("ZIP Code")["Overall Rating"].mean().reset_index()

doctors = pd.read_csv(
    r"C:\Users\ZhaoQ\Desktop\cappybara\raw data\doctors_zip.csv", dtype={"zipcode": str}
)
doctors["zipcode"] = doctors["zipcode"].astype(str).str.zfill(5)

## rename for merge
expense.rename(columns={"Zip Code": "zipcode"}, inplace=True)
rate_inpatient.rename(columns={"ZIP Code": "zipcode"}, inplace=True)
rate_nursing.rename(columns={"ZIP Code": "zipcode"}, inplace=True)
doctors.rename(columns={"average_rating": "doctor_rating"}, inplace=True)

# convert the zip code columns to string and ensure leading zeros are retained
expense["zipcode"] = expense["zipcode"].astype(str)
rate_inpatient["zipcode"] = rate_inpatient["zipcode"].astype(str)
rate_nursing["zipcode"] = rate_nursing["zipcode"].astype(str)
doctors["zipcode"] = doctors["zipcode"].astype(str)

# convert the zip code columns to string and ensure leading zeros are retained
expense["zipcode"] = expense["zipcode"].astype(str).str.zfill(5)
rate_inpatient["zipcode"] = rate_inpatient["zipcode"].astype(str).str.zfill(5)
rate_nursing["zipcode"] = rate_nursing["zipcode"].astype(str).str.zfill(5)

## merge
merged_health = pd.merge(
    expense,
    rate_inpatient,
    on="zipcode",
    how="outer",
    suffixes=("_expense", "_inpatient"),
).fillna(0)
merged_health = pd.merge(merged_health, rate_nursing, on="zipcode", how="outer").fillna(
    0
)
merged_health = pd.merge(merged_health, doctors, on="zipcode", how="outer").fillna(0)


# Load the datasets (make sure to replace the file paths with your actual paths)
# Note: The separator and header arguments are assumptions; you may need to adjust them according to your data.
long = pd.read_csv(
    r"C:\Users\ZhaoQ\Desktop\cappybara\raw data\US Zip Codes from 2013 Government Data",
    sep=",",
    header=None,
    names=["ZIP", "LAT", "LNG"],
)

# Convert both 'zip_code' columns to string to avoid datatype mismatch
long["ZIP"] = long["ZIP"].astype(str)

# Merge the datasets using an inner join
health_with_loc = merged_health.merge(
    long, left_on="zipcode", right_on="ZIP", how="inner"
)


# convert the DataFrame to a GeoDataFrame
# assuming the coordinates are in the NAD83 system
gdf_points = gpd.GeoDataFrame(
    health_with_loc,
    geometry=gpd.points_from_xy(health_with_loc.LNG, health_with_loc.LAT),
)
gdf_points.set_crs(epsg=4269, inplace=True)

# read the shapefile
gdf_polygons = gpd.read_file(
    r"C:\Users\ZhaoQ\Desktop\cappybara\tl_2020_acta_shapefile\tl_2020_us_zcta520.shp"
)


# ensure both GeoDataFrames have the same CRS
gdf_points.to_crs(gdf_polygons.crs, inplace=True)

# Perform the spatial join
gdf_merged = gpd.sjoin(gdf_points, gdf_polygons, how="left", predicate="within")


# put the zcta_code column in the first position
health_with_loc["ZCTA5CE20"] = gdf_merged["ZCTA5CE20"].astype(str)
health_with_loc.rename(columns={"ZCTA5CE20": "zcta_code"}, inplace=True)

columns_to_drop = ["zipcode", "ZIP", "LAT", "LNG"]
health_with_loc.drop(columns=columns_to_drop, inplace=True)
health_with_loc.to_csv("total_health.csv", index=False)


# Load the data
demand = pd.read_csv(r"C:\Users\ZhaoQ\Desktop\cappybara\pop_demand_uniform.csv")
health = pd.read_csv(
    r"C:\Users\ZhaoQ\Desktop\cappybara\total_health.csv", dtype={"zcta_code": str}
)

# Find zcta_codes that are in demand but not in health
unique_zcta = demand[~demand["zcta_code"].isin(health["zcta_code"])]["zcta_code"]

# Create a new DataFrame with the same columns as health and initialize with 0
new_rows = pd.DataFrame(0, index=unique_zcta.index, columns=health.columns)
# Set the zcta_code column with the unique values found in demand
new_rows["zcta_code"] = unique_zcta.values

# Append the new_rows to the health DataFrame
health_updated = pd.concat([health, new_rows], ignore_index=True)

# Fill any NaN values with 0
health_updated.fillna(0, inplace=True)

## deal with the missing data with neighbors
# Load shapefile into GeoDataFrame
gdf = gpd.read_file(
    r"C:\Users\ZhaoQ\Desktop\cappybara\tl_2020_acta_shapefile\tl_2020_us_zcta520.shp"
)

# Define columns of interest
columns_of_interest = [
    "hospital beds",
    "hospital cost per day",
    "nurse beds",
    "nurse cost per day",
    "home cost per visit",
    "Summary star rating",
    "Overall Rating",
    "num_doctors",
    "doctor_rating",
]

# Call the function with the optimized approach
updated_health_data = update_health_data_with_neighbors(
    gdf, health_updated, "zcta_code", columns_of_interest
)

# save the updated health data to a new CSV file
updated_health_data.to_csv("health_geo.csv", index=False)

# Load the data
demand = pd.read_csv(
    r"C:\Users\ZhaoQ\Desktop\cappybara\pop_demand_uniform.csv", dtype={"zcta_code": str}
)
health = pd.read_csv(
    r"C:\Users\ZhaoQ\Desktop\cappybara\health_geo.csv", dtype={"zcta_code": str}
)

columns_to_aggregate = health.columns.drop("zcta_code")
health_grouped = health.groupby("zcta_code")[columns_to_aggregate].mean().reset_index()
aggregations = {
    col: "mean" for col in columns_to_aggregate if health[col].dtype != "object"
}
health = health.groupby("zcta_code").agg(aggregations).reset_index()

# Check for any potential whitespace or formatting issues
demand["zcta_code"] = demand["zcta_code"].str.strip()
health["zcta_code"] = health["zcta_code"].str.strip()

# Create a list of zcta_codes from the demand DataFrame
zcta_codes_from_demand = demand["zcta_code"].unique()

# Filter the health DataFrame to only include rows with zcta_code present in the demand DataFrame
filtered_health = health[health["zcta_code"].isin(zcta_codes_from_demand)]

# Check the number of unique zcta_codes in the filtered_health DataFrame
print(
    f"Unique zcta_codes in filtered_health: {len(filtered_health['zcta_code'].unique())}"
)
print(f"Unique zcta_codes expected: {len(zcta_codes_from_demand)}")

# If there is a mismatch, we can investigate further:
if len(filtered_health["zcta_code"].unique()) != len(zcta_codes_from_demand):
    # Check which zcta_codes are missing
    missing_zcta_codes = set(zcta_codes_from_demand) - set(
        filtered_health["zcta_code"].unique()
    )
    print(f"Missing zcta_codes: {missing_zcta_codes}")

filtered_health.to_csv("filtered_health.csv", index=False)
