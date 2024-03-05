'''
Writen by Qi Zhao 
'''

## Data Clean for Census Data and Cost Data
# ## data clean for census data(all from ACS in 2022)
import pandas as pd
import os
import numpy as np
from functools import reduce


# Function to extract the ZIP code from the column name
def extract_zip(col_name):
    parts = col_name.split("!!")
    if len(parts) > 1:
        return parts[0][-5:]
    return col_name


## load data
pop = pd.read_csv(
    "C:\\Users\\ZhaoQ\\Desktop\\cappybara\\raw data\\data from ACS\\pop_raw.csv"
)

social = pd.read_csv(
    "C:\\Users\\ZhaoQ\\Desktop\\cappybara\\raw data\\data from ACS\\social_char_raw.csv"
)

income = pd.read_csv(
    "C:\\Users\\ZhaoQ\\Desktop\\cappybara\\raw data\\data from ACS\\income_raw.csv"
)

work = pd.read_csv(
    "C:\\Users\\ZhaoQ\\Desktop\\cappybara\\raw data\\data from ACS\\work_raw.cs"
)

poverty = pd.read_csv(
    "C:\\Users\\ZhaoQ\\Desktop\\cappybara\\raw data\\data from ACS\\poverty_raw.csv"
)

insurance = pd.read_csv(
    "C:\\Users\\ZhaoQ\\Desktop\\cappybara\\raw data\\data from ACS\\insurance_raw.csv"
)

private = pd.read_csv(
    "C:\\Users\\ZhaoQ\\Desktop\\cappybara\\raw data\\data from ACS\\private_insu_raw.csv"
)

public = pd.read_csv(
    "C:\\Users\\ZhaoQ\\Desktop\\cappybara\\raw data\\data from ACS\\public_insu_raw.csv"
)

hos_cost = pd.read_csv(
    "C:\\Users\\ZhaoQ\\Desktop\\cappybara\\raw data\\CostReport_2021_Final.csv"
)

nurse_cost = pd.read_csv(
    "C:\\Users\\ZhaoQ\\Desktop\\cappybara\\raw data\\CostReportsnf_Final_21.csv"
)

home_cost = pd.read_csv(
    "C:\\Users\\ZhaoQ\\Desktop\\cappybara\\raw data\\Home_Health_Agency_Cost_Report_2021.csv"
)

## population data clean
# select those columns with "estimate" and delete the others
columns_with_estimate = ["Label (Grouping)"] + [
    col for col in pop.columns if "Estimate" in col
]
pop_filtered = pop[columns_with_estimate]

# extact zip code
pop_filtered.columns = [extract_zip(col) for col in pop_filtered.columns]

# keep specific factors
rows_to_keep = [0, 3, 17] + list(range(65, 71)) + [73]
pop_cleaned = pop_filtered.iloc[rows_to_keep]

# transpose
pop_transposed = pop_cleaned.T
pop_transposed.columns = pop_transposed.iloc[0]
pop_transposed = pop_transposed.drop(pop_transposed.index[0])
pop_transposed.reset_index(inplace=True)
pop_transposed.rename(columns={"index": "zcta_code"}, inplace=True)

# check the type of each variable
for col in pop_transposed.columns:
    print(f"Column {col}: {pop_transposed[col].dtype}")

# convert object data into integer
for col in pop_transposed.columns:
    if col != "zcta_code":
        pop_transposed[col] = pd.to_numeric(
            pop_transposed[col].str.replace(",", ""), errors="coerce"
        )
        pop_transposed[col].fillna(0, inplace=True)
        pop_transposed[col] = pop_transposed[col].round(1)

# calculate race rate
pop_transposed["white rate"] = pop_transposed.iloc[:, 4] / pop_transposed.iloc[:, 1]
pop_transposed["black rate"] = pop_transposed.iloc[:, 5] / pop_transposed.iloc[:, 1]
pop_transposed["native rate"] = pop_transposed.iloc[:, 6] / pop_transposed.iloc[:, 1]
pop_transposed["asian rate"] = pop_transposed.iloc[:, 7] / pop_transposed.iloc[:, 1]
pop_transposed["other race rate"] = (
    pop_transposed.iloc[:, 8] + pop_transposed.iloc[:, 9]
) / pop_transposed.iloc[:, 1]
pop_transposed["hispanic rate"] = pop_transposed.iloc[:, 10] / pop_transposed.iloc[:, 1]

# clean the data again
pop_transposed.drop(pop_transposed.columns[4:11], axis=1, inplace=True)
pop_transposed.columns.values[2] = "sex ratio"
pop_transposed.columns.values[3] = "median age"

## social data clean
# select those columns with "estimate" and delete the others
columns_with_estimate = ["Label (Grouping)"] + [
    col for col in social.columns if "Estimate" in col
]
social_filtered = social[columns_with_estimate]

# Apply the function to each column name
social_filtered.columns = [extract_zip(col) for col in social_filtered.columns]

# keep specific factors
rows_to_keep = [6, 10] + list(range(14, 18)) + [66, 80, 81, 169, 170, 171]
social_cleaned = social_filtered.iloc[rows_to_keep]

# transpose
social_transposed = social_cleaned.T
social_transposed.columns = social_transposed.iloc[0]
social_transposed = social_transposed.drop(social_transposed.index[0])
social_transposed.reset_index(inplace=True)
social_transposed.rename(columns={"index": "zcta_code"}, inplace=True)

# check the type of each variable
for col in social_transposed.columns:
    print(f"Column {col}: {social_transposed[col].dtype}")

# convert object data into integer
for col in social_transposed.columns:
    if col != "zcta_code":
        social_transposed[col] = pd.to_numeric(
            social_transposed[col].str.replace(",", ""), errors="coerce"
        )
        social_transposed[col].fillna(0, inplace=True)
        social_transposed[col] = social_transposed[col].round(1)

social_transposed["disability rate"] = (
    social_transposed.iloc[:, 9] / social_transposed.iloc[:, 8]
)
social_transposed["computer rate"] = (
    social_transposed.iloc[:, 11] / social_transposed.iloc[:, 10]
)
social_transposed["internet rate"] = (
    social_transposed.iloc[:, 12] / social_transposed.iloc[:, 10]
)

# clean the data again
social_transposed.drop(social_transposed.columns[8:13], axis=1, inplace=True)
social_transposed.columns.values[1] = "male alone house"
social_transposed.columns.values[2] = "female alone house"
social_transposed.columns.values[3] = "house with child"
social_transposed.columns.values[4] = "house with old"


## income data clean
# Begin with the columns that don't require a condition check
columns_with_estimate = ["Geography", "Geographic Area Name"]

# Extend the list with columns that contain "Estimate" but not "RACE"
columns_with_estimate.extend(
    [col for col in income.columns if "Estimate" in col and "RACE" not in col]
)

# Now, use this list to filter the DataFrame
income_filtered = income[columns_with_estimate]
income_filtered = income_filtered.copy()

# The rest of your code for replacing and dropping NaNs seems fine.
income_filtered.replace("(X)", np.nan, inplace=True)
income_filtered.dropna(axis=1, how="all", inplace=True)

# clean the data
income_filtered = income_filtered.iloc[:, :6]
income_filtered["zcta_code"] = income_filtered["Geographic Area Name"].apply(
    lambda x: x[-5:]
)
income_filtered.drop("Geographic Area Name", axis=1, inplace=True)

# edit column name
new_columns = {}
for col in income_filtered.columns:
    if col.startswith("Estimate!!Number!!HOUSEHOLD INCOME BY AGE OF HOUSEHOLDER!!"):
        age_range = col.split("!!")[-1]
        new_columns[col] = f"median income {age_range}"

# rename
income_filtered.rename(columns=new_columns, inplace=True)


## employment data clean
# Begin with the columns that don't require a condition check
columns_with_estimate = ["Geography", "Geographic Area Name"]

# Extend the list with columns that contain "Estimate" but not "RACE"
columns_with_estimate.extend([col for col in work.columns if "Estimate" in col])

# Now, use this list to filter the DataFrame
work_filtered = work[columns_with_estimate]
work_filtered = work_filtered.copy()

# The rest of your code for replacing and dropping NaNs seems fine.
work_filtered.replace("(X)", np.nan, inplace=True)
work_filtered.dropna(axis=1, how="all", inplace=True)

# clean data and keep specific column
target_column = "Estimate!!Percent!!Population 16 to 64 years!!Workers 16 to 64 years who worked full-time, year-round"

columns_to_keep = work_filtered.columns[:3].tolist() + [target_column]

work_filtered = work_filtered.loc[:, columns_to_keep]
work_filtered["zcta_code"] = work_filtered["Geographic Area Name"].apply(
    lambda x: x[-5:]
)
work_filtered.drop("Geographic Area Name", axis=1, inplace=True)
work_filtered.columns.values[1] = "work population"
work_filtered.columns.values[2] = "full time percent"


## poverty data clean
# Begin with the columns that don't require a condition check
columns_with_estimate = ["Geography", "Geographic Area Name"]

# Extend the list with columns that contain "Estimate" but not "RACE"
columns_with_estimate.extend(
    [col for col in poverty.columns if "Estimate" in col and "RACE" not in col]
)

# Now, use this list to filter the DataFrame
poverty_filtered = poverty[columns_with_estimate]
poverty_filtered = poverty_filtered.copy()

# The rest of your code for replacing and dropping NaNs seems fine.
poverty_filtered.replace("(X)", np.nan, inplace=True)
poverty_filtered.dropna(axis=1, how="all", inplace=True)

# clean data and keep specific column
target_columns = [
    "Estimate!!Total!!Households!!HOUSEHOLD INCOME IN THE PAST 12 MONTHS (IN 2022 INFLATION-ADJUSTED DOLLARS)!!Median income (dollars)",
    "Estimate!!Percent!!Households!!POVERTY STATUS IN THE PAST 12 MONTHS!!Below poverty level",
    "Estimate!!Percent!!Households!!DISABILITY STATUS!!With one or more people with a disability",
    "Estimate!!Households receiving food stamps/SNAP!!Households",
]

columns_to_keep = poverty_filtered.columns[:2].tolist() + target_columns

poverty_filtered = poverty_filtered.loc[:, columns_to_keep]

poverty_filtered["zcta_code"] = poverty_filtered["Geographic Area Name"].apply(
    lambda x: x[-5:]
)
poverty_filtered.drop("Geographic Area Name", axis=1, inplace=True)

poverty_filtered.columns.values[1] = "median households income"
poverty_filtered.columns.values[2] = "poverty rate"
poverty_filtered.columns.values[3] = "households with disability"
poverty_filtered.columns.values[4] = "food stamps households"


## insurance data clean
# Begin with the columns that don't require a condition check
columns_with_estimate = ["Geography", "Geographic Area Name"]

# Extend the list with columns that contain "Estimate" but not "RACE"
columns_with_estimate.extend(
    [col for col in insurance.columns if "Estimate" in col and "RACE" not in col]
)

# Now, use this list to filter the DataFrame
insurance_filtered = insurance[columns_with_estimate]
insurance_filtered = insurance_filtered.copy()

# The rest of your code for replacing and dropping NaNs seems fine.
insurance_filtered.replace("(X)", np.nan, inplace=True)
insurance_filtered.dropna(axis=1, how="all", inplace=True)

# clean data and keep specific column
target_columns = [
    "Estimate!!Percent Insured!!Civilian noninstitutionalized population",
    "Estimate!!Percent Uninsured!!Civilian noninstitutionalized population",
]

columns_to_keep = insurance_filtered.columns[:2].tolist() + target_columns

insurance_filtered = insurance_filtered.loc[:, columns_to_keep]

insurance_filtered["zcta_code"] = insurance_filtered["Geographic Area Name"].apply(
    lambda x: x[-5:]
)
insurance_filtered.drop("Geographic Area Name", axis=1, inplace=True)

insurance_filtered.columns.values[1] = "insured rate"
insurance_filtered.columns.values[2] = "uninsured rate"


## public insurance data clean
# Begin with the columns that don't require a condition check
columns_with_estimate = ["Geography", "Geographic Area Name"]

# Extend the list with columns that contain "Estimate" but not "RACE"
columns_with_estimate.extend(
    [col for col in public.columns if "Estimate" in col and "RACE" not in col]
)

# Now, use this list to filter the DataFrame
public_filtered = public[columns_with_estimate]
public_filtered = public_filtered.copy()

# The rest of your code for replacing and dropping NaNs seems fine.
public_filtered.replace("(X)", np.nan, inplace=True)
public_filtered.dropna(axis=1, how="all", inplace=True)

# clean data and keep specific column
target_columns = [
    "Estimate!!Percent Public Coverage!!Civilian noninstitutionalized population",
    "Estimate!!Percent Public Coverage!!COVERAGE ALONE!!Public health insurance alone",
    "Estimate!!Percent Public Coverage!!COVERAGE ALONE!!Public health insurance alone!!Medicare coverage alone",
    "Estimate!!Percent Public Coverage!!COVERAGE ALONE!!Public health insurance alone!!Medicaid/means tested coverage alone",
]

columns_to_keep = public_filtered.columns[:2].tolist() + target_columns

public_filtered = public_filtered.loc[:, columns_to_keep]

public_filtered["zcta_code"] = public_filtered["Geographic Area Name"].apply(
    lambda x: x[-5:]
)
public_filtered.drop("Geographic Area Name", axis=1, inplace=True)

public_filtered.columns.values[1] = "public coverage"
public_filtered.columns.values[2] = "public health alone coverage"
public_filtered.columns.values[3] = "medicare alone coverage"
public_filtered.columns.values[4] = "medicaid alone coverage"


## private insurance data clean
# Begin with the columns that don't require a condition check
columns_with_estimate = ["Geography", "Geographic Area Name"]

# Extend the list with columns that contain "Estimate" but not "RACE"
columns_with_estimate.extend(
    [col for col in private.columns if "Estimate" in col and "RACE" not in col]
)

# Now, use this list to filter the DataFrame
private_filtered = private[columns_with_estimate]
private_filtered = private_filtered.copy()

# The rest of your code for replacing and dropping NaNs seems fine.
private_filtered.replace("(X)", np.nan, inplace=True)
private_filtered.dropna(axis=1, how="all", inplace=True)

# clean data and keep specific column
target_columns = [
    "Estimate!!Percent Private Coverage!!Civilian noninstitutionalized population",
    "Estimate!!Percent Private Coverage!!Civilian noninstitutionalized population!!COVERAGE ALONE!!Private health insurance alone",
    "Estimate!!Percent Private Coverage!!Civilian noninstitutionalized population!!COVERAGE ALONE!!Private health insurance alone!!Employer-based health insurance alone",
    "Estimate!!Percent Private Coverage!!Civilian noninstitutionalized population!!COVERAGE ALONE!!Private health insurance alone!!Direct-purchase health insurance alone",
]

columns_to_keep = private_filtered.columns[:2].tolist() + target_columns

private_filtered = private_filtered.loc[:, columns_to_keep]

private_filtered["zcta_code"] = private_filtered["Geographic Area Name"].apply(
    lambda x: x[-5:]
)
private_filtered.drop("Geographic Area Name", axis=1, inplace=True)

private_filtered.columns.values[1] = "private coverage"
private_filtered.columns.values[2] = "private health alone coverage"
private_filtered.columns.values[3] = "employer-based alone coverage"
private_filtered.columns.values[4] = "personal insurance alone coverage"


# merige all cleaned dataframe from ACS
acs = [
    pop_transposed,
    social_transposed,
    income_filtered,
    work_filtered,
    poverty_filtered,
    insurance_filtered,
    public_filtered,
    private_filtered,
]


def merge_acs(left, right):
    common_cols = list(set(left.columns) & set(right.columns))
    common_cols_to_keep = [
        col for col in common_cols if col not in ["zcta_code", "Geography"]
    ]
    merged_acs = pd.merge(
        left, right, on="zcta_code", how="outer", suffixes=("", "_drop")
    )
    merged_acs.drop(
        columns=[col for col in merged_acs.columns if col.endswith("_drop")],
        inplace=True,
    )

    return merged_acs


# save the final acs data
final_acs = reduce(merge_acs, acs)
final_acs.columns = final_acs.columns.str.strip()
final_acs.to_csv("final_acs.csv", index=False)


# # Data Clean for Cost data (2021)
## hospital cost data clean
hos_cost_cook = hos_cost[
    (hos_cost["State Code"] == "IL")
    & ((hos_cost["County"] == "COOK") | pd.isna(hos_cost["County"]))
]

# clean data and keep specific column
target_columns = [
    "Zip Code",
    "Number of Beds",
    "Total Bed Days Available",
    "Total Unreimbursed and Uncompensated Care",
    "Total Costs",
    "Combined Outpatient + Inpatient Total Charges",
    "Medicaid Charges",
]

hos_cost_cook = hos_cost_cook.loc[:, target_columns]

# unique name for hospital
hos_cost_cook.columns.values[1] = "hospital beds"
hos_cost_cook.columns.values[2] = "hospital days"
hos_cost_cook.columns.values[3] = "hospital unreimbursed care"
hos_cost_cook.columns.values[4] = "hospital cost"
hos_cost_cook.columns.values[5] = "hospital charges"
hos_cost_cook.columns.values[6] = "hospital medicaid charges"

# make sure all the data is right
hos_cost_cook = hos_cost_cook.applymap(
    lambda x: abs(x) if isinstance(x, (int, float)) and x < 0 else x
)

# zip code strip
hos_cost_cook["Zip Code"] = hos_cost_cook["Zip Code"].astype(str)
hos_cost_cook["Zip Code"] = hos_cost_cook["Zip Code"].str[:5]

# create new criteria
hos_cost_cook["hospital medicaid in charge"] = (
    hos_cost_cook.iloc[:, 6] / hos_cost_cook.iloc[:, 5]
)
hos_cost_cook["hospital cost per day"] = (
    hos_cost_cook.iloc[:, 4] / hos_cost_cook.iloc[:, 2]
)

# aggregate the data by zip_code
# covert na to 0
hos_cost_cook_filled = hos_cost_cook.fillna(0)

# group by zip_code and add them together
hos_cost_cook_grouped = hos_cost_cook_filled.groupby("Zip Code").sum()
hos_cost_cook_grouped = hos_cost_cook_grouped.reset_index()


## nurse cost data clean
nurse_cost_cook = nurse_cost[
    (nurse_cost["State Code"] == "IL")
    & ((nurse_cost["County"] == "COOK") | pd.isna(hos_cost["County"]))
]

# clean data and keep specific column
target_columns = [
    "Zip Code",
    "Total Days Total",
    "Number of Beds",
    "Total Costs",
    "Total Charges",
]

nurse_cost_cook = nurse_cost_cook.loc[:, target_columns]

# unique name for skilled nurse
nurse_cost_cook.columns.values[1] = "nurse days"
nurse_cost_cook.columns.values[2] = "nurse beds"
nurse_cost_cook.columns.values[3] = "nurse costs"
nurse_cost_cook.columns.values[4] = "nurse charges"

# make sure all the data is right
nurse_cost_cook = nurse_cost_cook.applymap(
    lambda x: abs(x) if isinstance(x, (int, float)) and x < 0 else x
)

# zip code strip
nurse_cost_cook["Zip Code"] = nurse_cost_cook["Zip Code"].astype(str)
nurse_cost_cook["Zip Code"] = nurse_cost_cook["Zip Code"].str[:5]

# create new criteria
nurse_cost_cook["nurse cost per day"] = (
    nurse_cost_cook.iloc[:, 3] / nurse_cost_cook.iloc[:, 1]
)
nurse_cost_cook["nurse cost in charge"] = (
    nurse_cost_cook.iloc[:, 3] / nurse_cost_cook.iloc[:, 4]
)

# aggregate the data by zip_code
# covert na to 0
nurse_cost_cook_filled = nurse_cost_cook.fillna(0)

# group by zip_code and add them together
nurse_cost_cook_grouped = nurse_cost_cook_filled.groupby("Zip Code").sum()
nurse_cost_cook_grouped = nurse_cost_cook_grouped.reset_index()


## home health cost data clean
home_cost_il = home_cost[(home_cost["State Code"] == "IL")]

# clean data and keep specific column
target_columns = [
    "Zip Code",
    "Total, Total Visits",
    "Total Cost",
    "Total Episodes-Total Charges",
]

home_cost_il = home_cost_il.loc[:, target_columns]

# unique name for home health service
home_cost_il.columns.values[1] = "home visits"
home_cost_il.columns.values[2] = "home costs"
home_cost_il.columns.values[3] = "home charges"

# make sure all the data is right
home_cost_il = home_cost_il.applymap(
    lambda x: abs(x) if isinstance(x, (int, float)) and x < 0 else x
)

# create new criteria
home_cost_il["home cost per visit"] = home_cost_il.iloc[:, 2] / home_cost_il.iloc[:, 1]
home_cost_il["home charge per visit"] = (
    home_cost_il.iloc[:, 3] / home_cost_il.iloc[:, 1]
)
home_cost_il["home charge in cost"] = home_cost_il.iloc[:, 3] / home_cost_il.iloc[:, 2]

# strip zip code
home_cost_il["Zip Code"] = home_cost_il["Zip Code"].astype(str)
home_cost_il["Zip Code"] = home_cost_il["Zip Code"].str[:5]

# aggregate the data by zip_code
# covert na to 0
home_cost_il_filled = home_cost_il.fillna(0)

# group by zip_code and add them together
home_cost_il_grouped = home_cost_il_filled.groupby("Zip Code").sum()
home_cost_il_grouped = home_cost_il_grouped.reset_index()

# merige all cleaned dataframe for health expenses
health_expen = [hos_cost_cook_grouped, nurse_cost_cook_grouped, home_cost_il_grouped]

health_expen = reduce(
    lambda left, right: pd.merge(left, right, on="Zip Code", how="outer"), health_expen
)
health_expen.to_csv("health_expen.csv", index=False)


# # Final Clean before analysis
finalacs_clean = pd.read_csv(r"C:\Users\ZhaoQ\Desktop\cappybara\final_acs.csv")
columns_to_drop = [
    "black rate",
    "native rate",
    "asian rate",
    "other race rate",
    "hispanic rate",
    "male alone house",
    "female alone house",
    "Population 25 years and over",
    "median income 15 to 24 years",
    "median income 25 to 44 years",
    "median income 45 to 64 years",
    "median income 65 years and over",
    "median income 15 to 24 years",
    "Geography",
    "Average family size",
    "insured rate",
]
finalacs_clean.drop(columns=columns_to_drop, inplace=True)
finalacs_clean = finalacs_clean.iloc[:, :-8]

finalacs_clean["need_service_households"] = (
    finalacs_clean["house with child"] + finalacs_clean["house with old"]
) / (finalacs_clean["Total population"] / finalacs_clean["Average household size"])
finalacs_clean["non_white_rate"] = 1 - finalacs_clean["white rate"]
finalacs_clean["worker rate"] = (
    finalacs_clean["work population"] / finalacs_clean["Total population"]
)
finalacs_clean.drop(
    columns=[
        "house with child",
        "house with old",
        "Average household size",
        "white rate",
        "work population",
    ],
    inplace=True,
)

finalacs_clean.to_csv("pop_demand.csv", index=False)
