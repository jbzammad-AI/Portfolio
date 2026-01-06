import numpy as np

def normalize_column(col):
    return (col - np.min(col)) / (np.max(col) - np.min(col))
