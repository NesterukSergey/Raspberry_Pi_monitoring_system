import pandas as pd
from pathlib import Path


def write_csv(df, file, sort=True):
    if 'DataFrame' not in str(type(df)):
        try:
            if sort:
                df = _sort_dict(df)
            df = _dict2df(df)
        except Exception as e:
            raise UserWarning('df must be DataFrame or dict', e)

    if Path(file).exists():
        df.to_csv(file, index=0, mode='a', header=False)
    else:
        df.to_csv(file, index=0)


def _dict2df(d):
    for k in d:
        if 'list' not in str(type(d[k])):
            d[k] = [d[k]]

    return pd.DataFrame(d)


def _sort_dict(d):
    sorted_cols = sorted(d.keys(), key=lambda x: x.lower())
    d_sorted = {}
    for k in sorted_cols:
        d_sorted[k] = d[k]

    return d_sorted


def read_csv(file):
    if not Path(file).exists():
        raise FileNotFoundError('No such .csv file: ' + str(file))
    else:
        df = pd.read_csv(file)
        return df
