import pandas as pd
from haversine import haversine

def load_data():
    cases = pd.read_csv("data/raw/cases.csv")
    tutors = pd.read_csv("data/raw/tutors.csv")
    results = pd.read_csv("data/raw/results.csv")
    return cases, tutors, results

def merge_datasets(cases, tutors, results):
    df = cases.merge(results, on="case_id").merge(tutors, on="tutor_id")
    return df

def compute_distance(row):
    return haversine((row['case_lat'], row['case_lon']), 
                     (row['tutor_lat'], row['tutor_lon']))

def preprocess(df):
    df = df.drop_duplicates()
    df['distance_km'] = df.apply(compute_distance, axis=1)
    df['price_gap'] = abs(df['tutor_rate'] - df['case_budget'])
    # Add more feature engineering here
    return df
