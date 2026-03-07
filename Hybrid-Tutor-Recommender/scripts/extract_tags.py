from src.tagging import extract_tags
import pandas as pd

df = pd.read_csv("data/processed/merged_data.csv")
df['case_tags'] = df['case_description'].apply(extract_tags)
df['tutor_tags'] = df['tutor_bio'].apply(extract_tags)
df.to_csv("data/processed/merged_data_with_tags.csv", index=False)
print("Tags extracted!")
