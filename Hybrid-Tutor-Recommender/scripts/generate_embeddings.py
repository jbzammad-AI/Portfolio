from src.embeddings import get_embedding, reduce_embeddings
import pandas as pd

df = pd.read_csv("data/processed/merged_data.csv")
texts = df['case_description'].tolist() + df['tutor_bio'].tolist()
embeddings = [get_embedding(t) for t in texts]
reduced = reduce_embeddings(embeddings)
print("Embeddings generated and reduced!")
