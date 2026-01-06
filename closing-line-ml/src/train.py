def train(models, X, y):
    fitted = {}
    for name, model in models.items():
        model.fit(X, y)
        fitted[name] = model
    return fitted
