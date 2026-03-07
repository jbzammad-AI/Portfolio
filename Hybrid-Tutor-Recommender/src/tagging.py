import pandas as pd
from src.tagging import extract_tags

cases = pd.read_csv("data/raw/cases.csv")
tutors = pd.read_csv("data/raw/tutors.csv")

# Extract tags
cases['case_tags'] = cases['case_description'].apply(extract_tags)
tutors['tutor_tags'] = tutors['tutor_bio'].apply(extract_tags)

# Save for later
cases.to_csv("data/processed/cases_with_tags.csv", index=False)
tutors.to_csv("data/processed/tutors_with_tags.csv", index=False)
print("✅ Tags extracted")
