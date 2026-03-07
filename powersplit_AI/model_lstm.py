# model_lstm.py
import pandas as pd
import torch
from torch import nn
from sklearn.preprocessing import MinMaxScaler
import numpy as np

# Load dataset
df = pd.read_csv("power_split_dataset.csv")
data = df[["load_power", "fuel_cell_power", "battery_power", "supercap_power"]].values

# Normalize
scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()
X_scaled = scaler_X.fit_transform(data[:,0].reshape(-1,1))
y_scaled = scaler_y.fit_transform(data[:,1:])

# Create sequences for LSTM
seq_len = 20
def create_sequences(X, y, seq_len):
    X_seq, y_seq = [], []
    for i in range(len(X)-seq_len):
        X_seq.append(X[i:i+seq_len])
        y_seq.append(y[i+seq_len])
    return np.array(X_seq), np.array(y_seq)

X_seq, y_seq = create_sequences(X_scaled, y_scaled, seq_len)
X_seq = torch.tensor(X_seq, dtype=torch.float32)
y_seq = torch.tensor(y_seq, dtype=torch.float32)

# Split train/test
split = int(0.8*len(X_seq))
X_train, X_test = X_seq[:split], X_seq[split:]
y_train, y_test = y_seq[:split], y_seq[split:]

# Define LSTM model
class PowerSplitLSTM(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(input_size=1, hidden_size=64, batch_first=True)
        self.fc = nn.Linear(64, 3)
    def forward(self, x):
        out, _ = self.lstm(x)
        out = out[:, -1, :]
        return self.fc(out)

model = PowerSplitLSTM()
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# Training
epochs = 50
for epoch in range(epochs):
    model.train()
    optimizer.zero_grad()
    output = model(X_train)
    loss = criterion(output, y_train)
    loss.backward()
    optimizer.step()
    if (epoch+1)%10==0:
        print(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item():.6f}")

# Test
model.eval()
y_pred = model(X_test).detach().numpy()
y_pred = scaler_y.inverse_transform(y_pred)
y_true = scaler_y.inverse_transform(y_test)
mae = np.mean(np.abs(y_pred - y_true))
print(f"LSTM MAE: {mae:.2f} kW")

# Save predictions
np.savetxt("lstm_predictions.csv", np.hstack([y_true, y_pred]), delimiter=",",
           header="fc_actual,batt_actual,sc_actual,fc_pred,batt_pred,sc_pred", comments="")
