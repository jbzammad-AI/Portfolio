def split_by_season(df):
    train = df[df["season_file"].str.contains(
        "2017-2018|2018-2019|2019-2020|2020-2021|2021-2022"
    )]

    val = df[df["season_file"].str.contains("2022-2023")]

    test = df[df["season_file"].str.contains("2023-2024")]

    return train, val, test
