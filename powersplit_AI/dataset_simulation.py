# dataset_simulation.py
import numpy as np
import pandas as pd

np.random.seed(42)

# Number of time steps
n = 1000

# Simulate load demand (kW)
time = np.arange(n)
load_power = 50 + 10*np.sin(0.02*time) + 5*np.random.randn(n)  # base + variation

# Power split rules
fuel_cell_power = np.clip(0.6*load_power, 0, None)  # 60% base load
residual = load_power - fuel_cell_power
battery_power = np.clip(0.7*residual, 0, None)      # 70% of leftover
supercap_power = np.clip(residual - battery_power, 0, None)  # rest to supercap

# Create DataFrame
df = pd.DataFrame({
    "time": time,
    "load_power": load_power,
    "fuel_cell_power": fuel_cell_power,
    "battery_power": battery_power,
    "supercap_power": supercap_power
})

# Save CSV
df.to_csv("power_split_dataset.csv", index=False)
print("Sample dataset saved as 'power_split_dataset.csv'")
