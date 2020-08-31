import pandas as pd
from pathlib import Path

from monitoring_system.utils.csv import *
TIME_LIST = ['year', 'month', 'day', 'hour', 'minute', 'second']


def get_df_datetime(df):
    df['datetime'] = pd.to_datetime(df[TIME_LIST])
    return df


def get_nontime_cols(df):
    init_cols = df.columns
    time_list = TIME_LIST.copy()
    time_list.append('datetime')
    cols = [c for c in init_cols if c not in time_list]
    return cols
