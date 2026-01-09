import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tqdm import tqdm  # for progress bar

# ----------------------------
# 1. Load dataset
# ----------------------------
df = pd.read_csv('simulated_power_split.csv', parse_dates=['datetime'])
df.set_index('datetime', inplace=True)
print("Dataset loaded. Shape:", df.shape)

# ----------------------------
# 2. Use subset for faster testing
# ----------------------------
USE_SUBSET = True      # Set False to use full dataset
SUBSET_SIZE = 100000   # Number of rows for subset

if USE_SUBSET:
    df = df.sample(n=SUBSET_SIZE, random_state=42).sort_index()
    print(f"Using subset of {SUBSET_SIZE} rows for faster training.")

# ----------------------------
# 3. Random Forest Regression
# ----------------------------
X = df[['total_load']].values
y = df[['fuel_cell', 'battery', 'supercapacitor']].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

rf_models = []
y_pred_rf = []

print("\nTraining Random Forest models...")
for i, col in enumerate(['fuel_cell', 'battery', 'supercapacitor']):
    print(f"  Training RF for {col}...")
    rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train[:, i])
    y_pred_rf.append(rf.predict(X_test))
    rf_models.append(rf)
    print(f"  Done {col}")

y_pred_rf = np.column_stack(y_pred_rf)
mse_rf = mean_squared_error(y_test, y_pred_rf)
r2_rf = r2_score(y_test, y_pred_rf)
print(f"Random Forest MSE: {mse_rf:.4f}, R2: {r2_rf:.4f}")

# ----------------------------
# 4. Plot RF results
# ----------------------------
for i, col in enumerate(['fuel_cell', 'battery', 'supercapacitor']):
    plt.figure(figsize=(12,4))
    plt.plot(y_test[:100, i], label=f'Actual {col}')
    plt.plot(y_pred_rf[:100, i], label=f'RF Predicted {col}', linestyle='--')
    plt.legend()
    plt.title(f"Random Forest: {col} (first 100 points)")
    filename = f"RF_{col}.png"
    plt.savefig(filename)
    plt.close()
    print(f"Saved plot: {filename}")

# ----------------------------
# 5. LSTM
# ----------------------------
print("\nPreparing data for LSTM...")

scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()

X_scaled = scaler_X.fit_transform(X)
y_scaled = scaler_y.fit_transform(y)

def create_lstm_dataset(X, y, time_steps=10):
    Xs, ys = [], []
    for i in range(len(X)-time_steps):
        Xs.append(X[i:i+time_steps])
        ys.append(y[i+time_steps])
    return np.array(Xs), np.array(ys)

time_steps = 10
X_lstm, y_lstm = create_lstm_dataset(X_scaled, y_scaled, time_steps)
split_idx = int(len(X_lstm)*0.8)

X_train_lstm, X_test_lstm = X_lstm[:split_idx], X_lstm[split_idx:]
y_train_lstm, y_test_lstm = y_lstm[:split_idx], y_lstm[split_idx:]

# Build LSTM model
model = Sequential()
model.add(LSTM(50, activation='relu', input_shape=(time_steps, X_train_lstm.shape[2])))
model.add(Dense(3))
model.compile(optimizer='adam', loss='mse')

print("\nTraining LSTM model...")

# Custom training loop with tqdm for progress
EPOCHS = 15
BATCH_SIZE = 32
steps_per_epoch = int(np.ceil(len(X_train_lstm) / BATCH_SIZE))

for epoch in range(EPOCHS):
    print(f"Epoch {epoch+1}/{EPOCHS}")
    for i in tqdm(range(0, len(X_train_lstm), BATCH_SIZE), desc="Training batches"):
        X_batch = X_train_lstm[i:i+BATCH_SIZE]
        y_batch = y_train_lstm[i:i+BATCH_SIZE]
        model.train_on_batch(X_batch, y_batch)
print("LSTM training completed.")

y_pred_lstm_scaled = model.predict(X_test_lstm)
y_pred_lstm = scaler_y.inverse_transform(y_pred_lstm_scaled)
y_test_inv = scaler_y.inverse_transform(y_test_lstm)

mse_lstm = mean_squared_error(y_test_inv, y_pred_lstm)
r2_lstm = r2_score(y_test_inv, y_pred_lstm)
print(f"LSTM MSE: {mse_lstm:.4f}, R2: {r2_lstm:.4f}")

# ----------------------------
# 6. Plot LSTM results
# ----------------------------
for i, col in enumerate(['fuel_cell', 'battery', 'supercapacitor']):
    plt.figure(figsize=(12,4))
    plt.plot(y_test_inv[:100, i], label=f'Actual {col}')
    plt.plot(y_pred_lstm[:100, i], label=f'LSTM Predicted {col}', linestyle='--')
    plt.legend()
    plt.title(f"LSTM: {col} (first 100 points)")
    filename = f"LSTM_{col}.png"
    plt.savefig(filename)
    plt.close()
    print(f"Saved plot: {filename}")

# ----------------------------
# 7. Save all predictions to CSV
# ----------------------------
# Align LSTM predictions with RF test length
y_pred_lstm_aligned = y_pred_lstm[-len(y_pred_rf):]
y_test_lstm_aligned = y_test_inv[-len(y_pred_rf):]

predictions_df = pd.DataFrame({
    'total_load': X_test.flatten(),
    'actual_fuel_cell': y_test[:,0],
    'RF_fuel_cell': y_pred_rf[:,0],
    'LSTM_fuel_cell': y_pred_lstm_aligned[:,0],
    'actual_battery': y_test[:,1],
    'RF_battery': y_pred_rf[:,1],
    'LSTM_battery': y_pred_lstm_aligned[:,1],
    'actual_supercapacitor': y_test[:,2],
    'RF_supercapacitor': y_pred_rf[:,2],
    'LSTM_supercapacitor': y_pred_lstm_aligned[:,2],
})

predictions_df.to_csv("predictions_RF_LSTM.csv", index=False)
print("All predictions saved to predictions_RF_LSTM.csv")

print("\nAll done! ✅")
