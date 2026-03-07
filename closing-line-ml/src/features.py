def build_features(df, prediction_hours):
    df = df.copy()

    # Time until event start
    df["time_to_event"] = (
        df["event_start"] - df["timestamp"]
    ).dt.total_seconds() / 3600

    # Filter to prediction window
    df = df[df["time_to_event"] >= prediction_hours]

    # Line movement features
    df["line_change"] = df["current_line"] - df["opening_line"]
    df["line_change_rate"] = df["line_change"] / df["time_to_event"]

    return df
