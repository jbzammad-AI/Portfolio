# main.py
# ======================================
# Closing Line Prediction - Feasibility Pipeline
# ======================================

from src.load_data import load_data
from src.prepare import prepare_features
from src.split import split_by_season
from src.models import get_models
from src.train import train
from src.evaluate import evaluate

def main():
    print("Loading data...")
    df = load_data()

    print("Preparing features...")
    df = prepare_features(df)

    print("Available seasons:")
    print(df["season_file"].value_counts())

    print("Splitting data by season...")
    train_df, val_df, test_df = split_by_season(df)

    FEATURES = [
        "home_open",
        "draw_open",
        "away_open"
    ]

    TARGET = "target_closing_home"

    # Safety checks
    assert all(col in df.columns for col in FEATURES + [TARGET]), "Missing columns"
    assert len(train_df) > 0 and len(test_df) > 0, "Empty train/test split"

    X_train = train_df[FEATURES]
    y_train = train_df[TARGET]

    X_test = test_df[FEATURES]
    y_test = test_df[TARGET]

    print(f"Train samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")

    print("Training models...")
    models = get_models()
    fitted_models = train(models, X_train, y_train)

    print("\nEvaluation on OUT-OF-SAMPLE test set (2023–2024):")
    print("--------------------------------------------------")

    for name, model in fitted_models.items():
        metrics = evaluate(model, X_test, y_test)
        print(f"{name:15s} | MAE: {metrics['MAE']:.4f} | RMSE: {metrics['RMSE']:.4f}")

    print("\nPipeline completed successfully.")

if __name__ == "__main__":
    main()
