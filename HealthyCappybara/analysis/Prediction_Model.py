'''
Written by Hourui Guo
'''


import pandas as pd
import matplotlib.pyplot as plt
import seaborn
from sklearn.model_selection import cross_val_score, StratifiedKFold, train_test_split, GridSearchCV
import dmba
from sklearn.linear_model import LinearRegression, Lasso, Ridge
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, mean_squared_error, mean_squared_log_error, median_absolute_error, make_scorer
import numpy as np
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor


# #### Data Cleaning

# Load the CSV files
health = pd.read_csv('health_score_all.csv')
demand = pd.read_csv('demand.csv')
health_score_col = health[['zcta_code', 'combined_health_score', 'quantity_score', 'expenses_score', 'quality_score']]

# Perform the inner join on 'zcta_code'
demand_joined_df = pd.merge(demand, health_score_col, on='zcta_code', how='inner')

# Drop rows where combined health score == 0
demand_joined_df = demand_joined_df[demand_joined_df['combined_health_score']!=0]

# Drop weighted columns which is used for calculating scores.
drop_weighted = [col for col in demand_joined_df.columns if "weighted" in col]
drop_demand_score = [col for col in demand_joined_df.columns if "demand" in col] + ['Combined_Score']
demand_joined_df = demand_joined_df.drop(columns=drop_weighted + drop_demand_score)

# Correlation Matrix
health_score_cor = demand_joined_df.drop(['quantity_score', 'expenses_score', 'quality_score', 'zcta_code'], axis=1)
plt.figure(figsize=(12, 10))
seaborn.heatmap(health_score_cor.corr(), annot=False, cmap='coolwarm',fmt='.2f', linewidths=0.5)
plt.title('Correlation Matrix Heatmap')
plt.xticks(color='white')
plt.yticks(color='white')
# Set the facecolor of the figure to black
plt.gcf().set_facecolor('black')

# Set the color of the axes to black
ax = plt.gca()
ax.set_facecolor('black')
# Set the color of the spines to white
for _, spine in ax.spines.items():
    spine.set_color('black')

plt.show()


health_score_cor = demand_joined_df.drop(['quantity_score', 'expenses_score', 'quality_score', 'zcta_code'], axis=1)
plt.figure(figsize=(12, 10))
seaborn.heatmap(health_score_cor.corr(), annot=False, cmap='coolwarm',fmt='.2f', linewidths=0.5)
plt.title('Correlation Matrix Heatmap')

plt.show()


#### Combined Health Score

plt.figure(figsize=(10,5))
plt.hist(demand_joined_df['combined_health_score'][:1000], color='#D8BFD8')
plt.title('Distribution of Combined Health Score', color='white')  # Title with black color
plt.xticks(color='white')
plt.yticks(color='white')
plt.gcf().set_facecolor('black')

# Set the color of the axes to black
ax = plt.gca()
ax.set_facecolor('black')

plt.show()


plt.figure(figsize=(10,5))
plt.hist(demand_joined_df['combined_health_score'][:1000], color='lightblue')
plt.title('Distribution of Combined Health Score')

plt.show()


combined_health_score_predictor = demand_joined_df.drop(['combined_health_score', 
                                                         'quantity_score', 'expenses_score', 'quality_score', 'zcta_code'], axis=1)
Y = demand_joined_df['combined_health_score']

X_train, X_test, y_train, y_test = train_test_split(
    combined_health_score_predictor,Y,test_size = 0.2, random_state=1)

# Try Linear Regression Model
health_lm = LinearRegression()
health_lm.fit(X_train, y_train)

print (pd.DataFrame({'Predictor': combined_health_score_predictor.columns, 'coefficient': health_lm.coef_}))


#print performance measures (training data), dmba package provided by professor from another class
dmba.regressionSummary(y_train,health_lm.predict(X_train))


# The extremely high MPE and MAPE values indicate a potential issue with the model.

# Try Regularized linear regression model
lasso = Lasso(alpha = 10)
lasso.fit(X_train, y_train)
lasso_pred = lasso.predict(X_test)
mse = mean_squared_error(y_test, lasso_pred)
rmse = np.sqrt(mse)
print(f"Mean Squared Error: {mse}")
print(f"Root Mean Squared Error: {rmse}")


ridge = Ridge(alpha = 10)
ridge.fit(X_train, y_train)
ridge_pred = ridge.predict(X_test)
mse = mean_squared_error(y_test, ridge_pred)
rmse = np.sqrt(mse)
print(f"Mean Squared Error: {mse}")
print(f"Root Mean Squared Error: {rmse}")


# From the graph, the linear regression, and regularized linear regressions, we can see the certain predictors are not highly correlated with the possible target variable, and the relationship between the features and the target is not linear or is more complex. In this case, we might consider models that can capture non-linear relationships, interactions between features, or that can leverage ensemble techniques for improved prediction. 

# #### Decision Tree

decision_tree_model = DecisionTreeRegressor(random_state=42)
decision_tree_model.fit(X_train, y_train)


y_pred_decisiontree = decision_tree_model.predict(X_test)
mse = mean_squared_error(y_test, y_pred_decisiontree)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred_decisiontree)

print(f"Mean Squared Error: {mse}")
print(f"Root Mean Squared Error: {rmse}")
print(f"R-squared: {r2}")


# Try Cross-validation for relatively small dataset
scores = cross_val_score(decision_tree_model, combined_health_score_predictor, Y, cv=5, scoring='neg_mean_squared_error')
rmse_scores = np.sqrt(-scores)

print(f"Cross-validated RMSE scores: {rmse_scores}")
print(f"Mean RMSE: {np.mean(rmse_scores)}")


# Get feature importances
importances = decision_tree_model.feature_importances_

# Convert the importances into a DataFrame
feature_importance_df = pd.DataFrame({
    'feature': combined_health_score_predictor.columns,
    'importance': importances
}).sort_values(by='importance', ascending=False)

# Display the feature importance
print(feature_importance_df)

# Create a bar chart with the specified properties
plt.figure(figsize=(8, 10))

# Set the background to black
plt.gca().set_facecolor('black')
plt.gcf().set_facecolor('black')

# Set the labels to white
plt.xlabel('Importance', color='white')
plt.ylabel('Feature', color='white')
plt.title('Feature Importances', color='white')

# Change the bar color to light purple and edge color to white for visibility
plt.barh(feature_importance_df['feature'], 
         feature_importance_df['importance'], color='#D8BFD8', edgecolor='white')

# Change the color of the tick labels to white
plt.tick_params(colors='white')

# Show the plot
plt.show()


# Try hypertuning

# Define your decision tree model
decision_tree_model = DecisionTreeRegressor(random_state=42)

# Create a dictionary of all the parameters you want to tune
param_grid = {
    'max_depth': [None, 2, 4, 6, 8, 10],
    'min_samples_split': [2, 4, 6, 8],
    'min_samples_leaf': [1, 2, 4, 6],
}

# Create a GridSearchCV object
grid_search = GridSearchCV(estimator=decision_tree_model, param_grid=param_grid, 
                           cv=5, n_jobs=-1, scoring='neg_mean_squared_error', verbose=1)

# Fit the GridSearchCV object to the data
grid_search.fit(combined_health_score_predictor, Y)

# Get the best estimator
best_decision_tree_model = grid_search.best_estimator_

# Get the best score
best_score = np.sqrt(-grid_search.best_score_)
print(f"Best RMSE from GridSearchCV: {best_score}")

# Get the best parameters
best_parameters = grid_search.best_params_
print(f"Best parameters: {best_parameters}")


from sklearn.tree import DecisionTreeRegressor

best_parameters = {'max_depth': 2, 'min_samples_split': 6,'min_samples_leaf': 2}

# Initialize the DecisionTreeRegressor model with the best hyperparameters
best_decision_tree_model = DecisionTreeRegressor(
    max_depth=best_parameters['max_depth'],
    min_samples_split=best_parameters['min_samples_split'],
    min_samples_leaf=best_parameters['min_samples_leaf'],
    random_state=42
)

# Fit the best model to the entire dataset
best_decision_tree_model.fit(combined_health_score_predictor, Y)

predictions = best_decision_tree_model.predict(combined_health_score_predictor)


r2 = r2_score(Y, predictions)
mae = mean_absolute_error(Y, predictions)
mse = mean_squared_error(Y, predictions)
rmse = np.sqrt(mse)  # Root Mean Squared Error
msle = mean_squared_log_error(Y, predictions)
medae = median_absolute_error(Y, predictions)

# Print the metrics
print(f"R-squared: {r2:.2f}")
print(f"Mean Absolute Error (MAE): {mae:.2f}")
print(f"Mean Squared Error (MSE): {mse:.2f}")
print(f"Root Mean Squared Error (RMSE): {rmse:.2f}")
print(f"Mean Squared Log Error (MSLE): {msle:.2f}")
print(f"Median Absolute Error (MedAE): {medae:.2f}")


# #### Random Forest

# As we have a relatively small dataset, and we have a little unbalanced data, to avoid overfitting, let's try random forest.

rf_regressor = RandomForestRegressor(random_state=42)

# Fit the regressor to the training data
rf_regressor.fit(X_train, y_train)

# Predict on the test data
y_pred_rf = rf_regressor.predict(X_test)

# Calculate performance metrics on the test set
mse = mean_squared_error(y_test, y_pred_rf)
r2 = r2_score(y_test, y_pred_rf)

print(f"Test MSE: {mse}")
print(f"Test R-squared: {r2}")


# Get feature importances and sort them
importances = rf_regressor.feature_importances_
indices = np.argsort(importances)

# Rearrange feature names so they match the sorted feature importances
names = [X_train.columns[i] for i in indices]

# Create a plot
plt.figure(figsize=(10, 8))

# Create plot title
plt.title("Feature Importance of Attributes")

# Add bars
plt.barh(range(len(names)), importances[indices], color='#D8BFD8')

# Add feature names as y-axis labels
plt.yticks(range(len(names)), names)

# Add grid lines behind the bars
plt.grid(which='major', linestyle='-', linewidth='0.5', color='white', axis='x')

# Set the axes' face color to black
plt.gca().set_facecolor('black')

# Set the figure's face color to black
plt.gcf().set_facecolor('black')

# Change the label and axis colors to white
plt.xlabel('Importance', color='white')
plt.ylabel('Features', color='white')
plt.title('Feature Importance for the Random Forest Model', color='white')
plt.tick_params(colors='white')

# Show the plot
plt.show()


# Get feature importances and sort them
importances = rf_regressor.feature_importances_
indices = np.argsort(importances)

# Rearrange feature names so they match the sorted feature importances
names = [X_train.columns[i] for i in indices]

# Create a plot
plt.figure(figsize=(10, 8))

# Add bars
plt.barh(range(len(names)), importances[indices], color='lightblue')

# Add feature names as y-axis labels
plt.yticks(range(len(names)), names)

# Add grid lines behind the bars
plt.grid(which='major', linestyle='-', linewidth='0.5', axis='x')

plt.title('Feature Importance for the Random Forest Model')

# Show the plot
plt.show()


# Compute correlation matrix for X_train and y_train
correlation_matrix = pd.concat([X_train, y_train], axis=1).corr()

# Get the correlation of each feature with the target variable
target_correlations = correlation_matrix.iloc[:-1, -1].sort_values(ascending=False)
print(target_correlations)

