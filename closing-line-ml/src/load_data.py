import pandas as pd
from pathlib import Path

def load_data():
    files = sorted(Path("data/raw").glob("all-euro-data-*.xlsx"))
    dfs = []

    for f in files:
        df = pd.read_excel(f)
        df["season_file"] = f.name
        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)
