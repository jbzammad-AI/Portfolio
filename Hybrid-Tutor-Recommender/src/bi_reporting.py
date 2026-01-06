import pandas as pd

def niche_discovery(df):
    """Find rare skills or niches in tutor bios."""
    # Example: count niche tags
    niches = df['niche'].explode().value_counts()
    return niches

def supply_gap_analysis(df):
    """Compute weak supply areas."""
    supply_gap = df.groupby(['location', 'subject']).agg(
        request_count=('case_id', 'count'),
        success_count=('success', 'sum')
    )
    supply_gap['failure_rate'] = 1 - supply_gap['success_count']/supply_gap['request_count']
    return supply_gap

def dynamic_pricing_simulator(model, X, budgets):
    """Simulate success probability for different budgets."""
    results = []
    for b in budgets:
        X_temp = X.copy()
        X_temp['case_budget'] = b
        prob = model.predict_proba(X_temp)[:,1]
        results.append({'budget': b, 'probability': prob.mean()})
    return pd.DataFrame(results)
