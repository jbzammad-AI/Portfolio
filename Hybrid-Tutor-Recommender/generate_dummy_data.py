import pandas as pd
import numpy as np
import os

# Create folders if they don't exist
os.makedirs("data/raw", exist_ok=True)

# -----------------------------
# 1️⃣ Generate dummy cases
# -----------------------------
num_cases = 100
case_descriptions = [
    "A-Level Physics student, SEN-friendly",
    "IB Math tutoring required",
    "GCSE Chemistry tutoring, online",
    "English tutoring, SEN-friendly",
    "Medical interview prep",
    "Aviation studies tutoring",
    "Math Olympiad training"
]

cases = pd.DataFrame({
    'case_id': range(1, num_cases + 1),
    'case_description': np.random.choice(case_descriptions, num_cases),
    'case_budget': np.random.randint(30, 150, num_cases),
    'case_lat': np.random.uniform(22.28, 22.35, num_cases),  # Hong Kong approx
    'case_lon': np.random.uniform(114.15, 114.25, num_cases),
    'preferred_gender': np.random.choice(["Male", "Female", "Any"], num_cases)
})

cases.to_csv("data/raw/cases.csv", index=False)
print("✅ cases.csv generated")

# -----------------------------
# 2️⃣ Generate dummy tutors
# -----------------------------
num_tutors = 50
tutor_bios = [
    "Experienced Physics tutor, SEN-friendly",
    "Math tutor, IB and A-Level",
    "Chemistry tutor with exam success",
    "English tutor, SEN-friendly",
    "Medical interview preparation tutor",
    "Aviation studies expert tutor",
    "Math Olympiad specialist"
]

tutors = pd.DataFrame({
    'tutor_id': range(1, num_tutors + 1),
    'tutor_name': [f"Tutor_{i}" for i in range(1, num_tutors + 1)],
    'tutor_bio': np.random.choice(tutor_bios, num_tutors),
    'tutor_rate': np.random.randint(30, 150, num_tutors),
    'tutor_lat': np.random.uniform(22.28, 22.35, num_tutors),
    'tutor_lon': np.random.uniform(114.15, 114.25, num_tutors),
    'gender': np.random.choice(["Male", "Female"], num_tutors)
})

tutors.to_csv("data/raw/tutors.csv", index=False)
print("✅ tutors.csv generated")

# -----------------------------
# 3️⃣ Generate dummy results (historical matches)
# -----------------------------
num_results = 200  # number of historical match records

results = pd.DataFrame({
    'case_id': np.random.choice(cases['case_id'], num_results),
    'tutor_id': np.random.choice(tutors['tutor_id'], num_results),
    'success': np.random.choice([0, 1], num_results, p=[0.3, 0.7])  # 70% success rate
})

results.to_csv("data/raw/results.csv", index=False)
print("✅ results.csv generated")

print("\nAll dummy datasets are ready in data/raw/")
