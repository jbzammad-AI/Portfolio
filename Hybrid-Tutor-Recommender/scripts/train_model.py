from src.data_pipeline import load_data, merge_datasets, preprocess
from src.ranking_model import train_model
import pandas as pd

cases, tutors, results = load_data()
df = merge_datasets(cases, tutors, results)
df = preprocess(df)

X = df.drop(columns=['success', 'case_id', 'tutor_id'])
y = df['success']

model = train_model(X, y)
print("Model trained and saved!")
