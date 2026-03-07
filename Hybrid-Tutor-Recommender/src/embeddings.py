import openai
import numpy as np
from sklearn.decomposition import PCA
import os

# Optionally set API key via environment variable
# os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_KEY"

# -----------------------------
# Get embedding from OpenAI
# -----------------------------
def get_embedding(text, model="text-embedding-3-small"):
    """
    Returns a numeric embedding for a given text using OpenAI embeddings.
    """
    response = openai.Embedding.create(
        input=text,
        model=model
    )
    return np.array(response['data'][0]['embedding'])

# -----------------------------
# Dimensionality reduction
# -----------------------------
def reduce_embeddings(embeddings, n_components=32):
    """
    Reduce embedding dimensionality using PCA.
    """
    pca = PCA(n_components=n_components)
    reduced = pca.fit_transform(embeddings)
    return reduced
