import numpy as np


def average(lst):
    n = np.array(lst, dtype=float)
    n = n[np.isfinite(n)]  # Remove Nones
    filtered = _reject_outliers(n, m=1)
    mean = filtered.mean()

    if not np.isnan(mean):
        return mean
    else:
        return None


def _reject_outliers(data, m=2):
    return data[abs(data - np.mean(data)) <= m * np.std(data)]
