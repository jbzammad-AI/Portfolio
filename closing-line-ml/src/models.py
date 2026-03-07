from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb

def get_models():
    return {
        "Ridge": Ridge(),
        "RandomForest": RandomForestRegressor(n_estimators=200, random_state=42),
        "XGBoost": xgb.XGBRegressor(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.05,
            random_state=42
        )
    }
