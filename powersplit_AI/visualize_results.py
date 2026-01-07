# visualize_results.py
import pandas as pd
import matplotlib.pyplot as plt

# Choose which predictions to plot
file = "rf_predictions.csv"   # or "lstm_predictions.csv"
df = pd.read_csv(file)

# Plot first 50 points
plt.figure(figsize=(12,6))
plt.plot(df["fc_actual"][:50], 'r', label="FC Actual")
plt.plot(df["fc_pred"][:50], 'r--', label="FC Predicted")
plt.plot(df["batt_actual"][:50], 'g', label="Battery Actual")
plt.plot(df["batt_pred"][:50], 'g--', label="Battery Predicted")
plt.plot(df["sc_actual"][:50], 'b', label="Supercap Actual")
plt.plot(df["sc_pred"][:50], 'b--', label="Supercap Predicted")
plt.xlabel("Time step")
plt.ylabel("Power (kW)")
plt.title("Power Split Predictions vs Actual")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
