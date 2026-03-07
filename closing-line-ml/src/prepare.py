def prepare_features(df):
    df = df.copy()

    df = df.dropna(subset=[
        "B365H", "B365D", "B365A",
        "B365CH"
    ])

    df["home_open"] = df["B365H"]
    df["draw_open"] = df["B365D"]
    df["away_open"] = df["B365A"]

    df["target_closing_home"] = df["B365CH"]

    return df
