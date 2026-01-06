import pandas as pd
from pathlib import Path

def load_all_seasons(data_dir="data/raw"):
    files = sorted(Path(data_dir).glob("all-euro-data-*"))
    dfs = []

    for f in files:
        print(f"Loading {f.name}")
        df = pd.read_excel(f)
        df["season_file"] = f.name
        dfs.append(df)

    data = pd.concat(dfs, ignore_index=True)
    return data
