## Writen by Qi Zhao ##

## Data Processing for rating and prediction model
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


## AHP method function
def calculate_composite_weights_with_consistency_check(matrix):
    n = matrix.shape[0]

    # check if the matrix is completely consistent (all elements are the same)
    if np.all(matrix == matrix[0, 0]):
        return np.ones(n) / n, 0

    # arithmetic mean
    arithmetic_means = matrix.mean(axis=0)
    # geometric mean
    geometric_means = np.exp(np.log(matrix).mean(axis=0))

    # eigenvector method and consistency check
    eigenvalues, eigenvector = np.linalg.eig(matrix)
    max_eigenvalue = np.max(eigenvalues.real)
    eigenvector_max = eigenvector[:, eigenvalues.real.argmax()].real
    eigenvector_normalized = eigenvector_max / np.sum(eigenvector_max.real)

    # calculate consistency index CI and consistency ratio CR
    ci = (max_eigenvalue - n) / (n - 1)
    ri = [0, 0, 0.58, 0.90, 1.12, 1.24, 1.32, 1.41, 1.45]
    cr = ci / ri[n - 1] if n <= len(ri) else 0

    if cr >= 0.1:
        raise ValueError(f"Consistency ratio is too high: CR={cr}")

    # normalized weights
    arithmetic_means_normalized = arithmetic_means / np.sum(arithmetic_means)
    geometric_means_normalized = geometric_means / np.sum(geometric_means)

    # composite weights
    composite_weights = (
        arithmetic_means_normalized
        + geometric_means_normalized
        + eigenvector_normalized
    ) / 3

    return composite_weights, cr


## EMW method function
def entropy_weight_method(df):
    """
    use entropy weight method to calculate the weights of different columns (indicators) in a DataFrame.
    :param df: pandas DataFrame, representing the decision matrix for which weights need to be calculated,
    where different columns represent different indicators.
    :return: weights array.
    """
    # standardize the data to ensure it is positive and normalize the columns
    matrix_normalized = df / df.sum()

    # calculate the entropy of each indicator
    epsilon = 1e-12
    matrix_entropy = -np.sum(
        matrix_normalized * np.log(matrix_normalized + epsilon), axis=0
    ) / np.log(len(df))

    # calculate the coefficient of variation for each indicator
    diff_coefficient = 1 - matrix_entropy

    # calculate the weights
    weights = diff_coefficient / diff_coefficient.sum()

    return weights


# Combined weights function
def calculate_combined_weights(ahp_weights, emw_weights, sub_criteria):
    combined_weights = {}

    for sub_weights, criteria in zip(ahp_weights, sub_criteria):
        for weight, column in zip(sub_weights, criteria):
            combined_weight = np.sqrt(weight * emw_weights[column])
            combined_weights[column] = combined_weight

    # normalize the combined weights
    total_weight = sum(combined_weights.values())
    for column in combined_weights:
        combined_weights[column] /= total_weight

    return combined_weights


# Extract the weights from the combined_weights dictionary and order them
def get_weight_vector(combined_weights, columns):
    return np.array([combined_weights[column] for column in columns])


### population demand score
# sustainability model: health service should match population demand, so we need to create a score to rate it
# population demand model:
## measure by 1, demographic factors; 2, vulnerbility factors 3, poverty factors  4, development factors;
## 1, total population/sex ratio/median age/non_white rate/
## 2, disability rate/households with disability/need_service_households
## 3, poverty rate/food stamps households/uninsured rate
## 4, median households income/full time percent/computer rate/internet rate

pop_demand = pd.read_csv(r"C:\Users\ZhaoQ\Desktop\cappybara\pop_demand.csv")

# standardize
need_uniform_cols = [
    "Total population",
    "sex ratio",
    "median age",
    "disability rate",
    "computer rate",
    "internet rate",
    "full time percent",
    "median households income",
    "poverty rate",
    "households with disability",
    "food stamps households",
    "uninsured rate",
    "need_service_households",
    "non_white_rate",
    "worker rate",
]

scaler = MinMaxScaler(feature_range=(0, 100))
for col in need_uniform_cols:
    if col in pop_demand.columns:
        pop_demand[col] = pd.to_numeric(pop_demand[col], errors="coerce")

pop_demand.fillna(0, inplace=True)

scaler = MinMaxScaler(feature_range=(0, 100))
pop_demand[need_uniform_cols] = scaler.fit_transform(pop_demand[need_uniform_cols])
pop_demand.to_csv("pop_demand_uniform.csv", index=False)

## weight by AHP for population demand
# define the criteria comparison matrix
criteria_matrix = np.array([[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 1]])

# define the sub-criteria comparison matrix - population demand
sub_criteria_population_matrix = np.array(
    [[1, 3, 5, 3], [1 / 3, 1, 3, 1], [1 / 5, 1 / 3, 1, 1 / 3], [1 / 3, 1, 1 / 3, 1]]
)

# define the sub-criteria comparison matrix - vulnerability demand
sub_criteria_vulberability_matrix = np.array([[1, 1, 1 / 5], [1, 1, 1 / 5], [5, 5, 1]])

# define the sub-criteria comparison matrix - poverty demand
sub_criteria_poverty_matrix = np.array([[1, 1 / 3, 3], [3, 1, 5], [1 / 3, 1 / 5, 1]])

# define the sub-criteria comparison matrix - development demand
sub_criteria_development_matrix = np.array([[1, 1], [1, 1]])

# calculate weights for population demand
criteria_weights = calculate_composite_weights_with_consistency_check(criteria_matrix)
population_weights = calculate_composite_weights_with_consistency_check(
    sub_criteria_population_matrix
)
vulnerability_weights = calculate_composite_weights_with_consistency_check(
    sub_criteria_vulberability_matrix
)
poverty_weights = calculate_composite_weights_with_consistency_check(
    sub_criteria_poverty_matrix
)
development_weights = calculate_composite_weights_with_consistency_check(
    sub_criteria_development_matrix
)

# calculate weights and only take the weight vector part
criteria_weights, _ = calculate_composite_weights_with_consistency_check(
    criteria_matrix
)
population_weights, _ = calculate_composite_weights_with_consistency_check(
    sub_criteria_population_matrix
)
vulnerability_weights, _ = calculate_composite_weights_with_consistency_check(
    sub_criteria_vulberability_matrix
)
poverty_weights, _ = calculate_composite_weights_with_consistency_check(
    sub_criteria_poverty_matrix
)
development_weights, _ = calculate_composite_weights_with_consistency_check(
    sub_criteria_development_matrix
)


## weight by EMW for population demand
pop_demand_uniform = pd.read_csv(
    r"C:\Users\ZhaoQ\Desktop\cappybara\pop_demand_uniform.csv"
)

# calculate weights
columns_to_exclude = ["zcta_code"]
indicator_columns = [
    col for col in pop_demand_uniform.columns if col not in columns_to_exclude
]
indicators_df = pop_demand_uniform[indicator_columns]
emw_weights = entropy_weight_method(indicators_df)

# combine two methods
# indicators and their corresponding AHP weights
sub_criteria = [
    ["Total population", "sex ratio", "median age", "non_white_rate"],
    ["disability rate", "households with disability", "need_service_households"],
    ["poverty rate", "food stamps households", "uninsured rate"],
    ["full time percent", "worker rate"],
]

ahp_weights = [
    population_weights,
    vulnerability_weights,
    poverty_weights,
    development_weights,
]


# calculate the combined weights for population demand
combined_weights = calculate_combined_weights(ahp_weights, emw_weights, sub_criteria)

# Multiply each column in pop_demand_uniform by its corresponding weight
for column, weight in combined_weights.items():
    pop_demand_uniform[column + "_weighted"] = pop_demand_uniform[column] * weight

# Sum the weighted columns to get the combined score
weighted_columns = [column + "_weighted" for column in combined_weights]
pop_demand_uniform["Combined_Score"] = pop_demand_uniform[weighted_columns].sum(axis=1)

# calculate the scores for different sub-criteria
pop_demand_uniform["demographic_demand"] = pop_demand_uniform[
    ["Total population", "sex ratio", "median age", "non_white_rate"]
].dot(
    get_weight_vector(
        combined_weights,
        ["Total population", "sex ratio", "median age", "non_white_rate"],
    )
)
pop_demand_uniform["vulnerability_demand"] = pop_demand_uniform[
    ["disability rate", "households with disability", "need_service_households"]
].dot(
    get_weight_vector(
        combined_weights,
        ["disability rate", "households with disability", "need_service_households"],
    )
)
pop_demand_uniform["poverty_demand"] = pop_demand_uniform[
    ["poverty rate", "food stamps households", "uninsured rate"]
].dot(
    get_weight_vector(
        combined_weights, ["poverty rate", "food stamps households", "uninsured rate"]
    )
)
pop_demand_uniform["development_demand"] = pop_demand_uniform[
    ["full time percent", "worker rate"]
].dot(get_weight_vector(combined_weights, ["full time percent", "worker rate"]))

# check the calculated scores and save the results
print(
    pop_demand_uniform[
        [
            "zcta_code",
            "demographic_demand",
            "vulnerability_demand",
            "poverty_demand",
            "development_demand",
        ]
    ]
)
pop_demand_uniform.to_csv("demand.csv", index=False)


# # # health service accessibility score
# Health Service Accessibility Score
## measure by 1, number of doctors/beds; 2, health expenditure; 3, health quality
## 1, number of doctors/beds
## 2, health expenditure: hospital expenditure/ home_expend/nursing expend
## 3, health quality: hospital rate/ nursing rate/ homecare agency rate/ doctor rate
health_geo = pd.read_csv(r"C:\Users\ZhaoQ\Desktop\cappybara\filtered_health.csv")

# standardize
need_uniform_cols = [
    "hospital beds",
    "hospital cost per day",
    "nurse beds",
    "nurse cost per day",
    "home cost per visit",
    "Summary star rating",
    "Overall Rating",
    "num_doctors",
    "doctor_rating",
    "home_rating",
]

scaler = MinMaxScaler(feature_range=(0, 100))
for col in need_uniform_cols:
    if col in pop_demand.columns:
        pop_demand[col] = pd.to_numeric(pop_demand[col], errors="coerce")

health_geo.fillna(0, inplace=True)

scaler = MinMaxScaler(feature_range=(0, 100))
health_geo[need_uniform_cols] = scaler.fit_transform(health_geo[need_uniform_cols])
health_geo.to_csv("health_geo_uniform.csv", index=False)

# weight by AHP for health service accessibility
# calculate the composite weights and check consistency
criteria_matrix = np.array([[1, 1, 1], [1, 1, 1], [1, 1, 1]])

# define the sub-criteria comparison matrix - service quantity
sub_criteria_quantity_matrix = np.array([[1, 2, 5], [1 / 2, 1, 3], [1 / 5, 1 / 3, 1]])

# define the sub-criteria comparison matrix - service expenses
sub_criteria_expenses_matrix = np.array([[1, 2, 5], [1 / 2, 1, 3], [1 / 5, 1 / 3, 1]])


# define the sub-criteria comparison matrix - service quality
sub_criteria_quality_matrix = np.array(
    [[1, 2, 5, 4], [1 / 2, 1, 3, 2], [1 / 5, 1 / 3, 1, 1 / 2], [1 / 3, 1 / 2, 2, 1]]
)

# calculate weights
criteria_weights = calculate_composite_weights_with_consistency_check(criteria_matrix)
quantity_weights = calculate_composite_weights_with_consistency_check(
    sub_criteria_quantity_matrix
)
expenses_weights = calculate_composite_weights_with_consistency_check(
    sub_criteria_expenses_matrix
)
quality_weights = calculate_composite_weights_with_consistency_check(
    sub_criteria_quality_matrix
)

# calculate weights and only take the weight vector part
criteria_weights, _ = calculate_composite_weights_with_consistency_check(
    criteria_matrix
)
quantity_weights, _ = calculate_composite_weights_with_consistency_check(
    sub_criteria_quantity_matrix
)
expenses_weights, _ = calculate_composite_weights_with_consistency_check(
    sub_criteria_expenses_matrix
)
quality_weights, _ = calculate_composite_weights_with_consistency_check(
    sub_criteria_quality_matrix
)


## weight by EMW for health service accessibility
health_geo_uniform = pd.read_csv(
    r"C:\Users\ZhaoQ\Desktop\cappybara\health_geo_uniform.csv"
)

# combine two methods
# indicators and their corresponding AHP weights
sub_criteria = [
    ["hospital beds", "nurse beds", "num_doctors"],
    ["hospital cost per day", "nurse cost per day", "home cost per visit"],
    ["Summary star rating", "Overall Rating", "doctor_rating", "home_rating"],
]


ahp_weights = [quantity_weights, expenses_weights, quality_weights]


# calculate the combined weights
combined_weights = calculate_combined_weights(ahp_weights, emw_weights, sub_criteria)

# Multiply each column in pop_demand_uniform by its corresponding weight
for column, weight in combined_weights.items():
    health_geo_uniform[column + "_weighted"] = health_geo_uniform[column] * weight

# Sum the weighted columns to get the combined score
weighted_columns = [column + "_weighted" for column in combined_weights]
health_geo_uniform["origin_health_score"] = health_geo_uniform[weighted_columns].sum(
    axis=1
)

# Now, print the combined score along with the zcta_code to verify
print(health_geo_uniform[["zcta_code", "origin_health_score"]])

# calculate the scores for different sub-criteria
health_geo_uniform["quantity_score"] = health_geo_uniform[
    ["hospital beds", "nurse beds", "num_doctors"]
].dot(
    get_weight_vector(combined_weights, ["hospital beds", "nurse beds", "num_doctors"])
)
health_geo_uniform["expenses_score"] = health_geo_uniform[
    ["hospital cost per day", "nurse cost per day", "home cost per visit"]
].dot(
    get_weight_vector(
        combined_weights,
        ["hospital cost per day", "nurse cost per day", "home cost per visit"],
    )
)
health_geo_uniform["quality_score"] = health_geo_uniform[
    ["Summary star rating", "Overall Rating", "doctor_rating", "home_rating"]
].dot(
    get_weight_vector(
        combined_weights,
        ["Summary star rating", "Overall Rating", "doctor_rating", "home_rating"],
    )
)

# check the calculated scores and save the results
print(
    health_geo_uniform[
        ["zcta_code", "quantity_score", "expenses_score", "quality_score"]
    ]
)
health_geo_uniform.to_csv("health_score.csv", index=False)
