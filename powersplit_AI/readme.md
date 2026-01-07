# AI-Based Power Split Prediction

This project predicts how power is split between Fuel Cell, Battery, and Supercapacitor based on load demand using machine learning.

## Folder structure
```
PowerSplitAI/
│
├── dataset_simulation.py      # Generates sample dataset
├── model_rf.py                # Random Forest baseline
├── model_lstm.py              # LSTM model
├── visualize_results.py       # Plot predictions vs actual
├── power_split_dataset.csv    # Generated dataset
├── README.md
└── requirements.txt           # Python dependencies
```

## Setup

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Generate dataset:
```
python dataset_simulation.py
```

3. Train Random Forest model:
```
python model_rf.py
```

4. Train LSTM model (optional):
```
python model_lstm.py
```

5. Visualize predictions:
```
python visualize_results.py
```

## Features
- Simulated dataset with load demand and power split
- Random Forest baseline
- LSTM deep learning model
- Visualization of predictions vs actual
- Ready for extension with more complex load profiles or constraints
