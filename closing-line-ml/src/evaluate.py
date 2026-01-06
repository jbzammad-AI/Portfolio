from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

def evaluate(model, X, y):
    preds = model.predict(X)
    return {
        "MAE": mean_absolute_error(y, preds),
        "RMSE": np.sqrt(mean_squared_error(y, preds))
    }
