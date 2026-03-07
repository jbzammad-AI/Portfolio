# model_rf.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

# Load dataset
df = pd.read_csv("power_split_dataset.csv")

# Features & target
X = df[["load_power"]].values
y = df[["fuel_cell_power", "battery_power", "supercap_power"]].values

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Random Forest Regressor for multi-output
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Evaluate
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
print(f"Random Forest MAE: {mae:.2f} kW")
print(f"Random Forest RMSE: {rmse:.2f} kW")

# Save predictions for plotting
np.savetxt("rf_predictions.csv", np.hstack([y_test, y_pred]), delimiter=",",
           header="fc_actual,batt_actual,sc_actual,fc_pred,batt_pred,sc_pred", comments="")
