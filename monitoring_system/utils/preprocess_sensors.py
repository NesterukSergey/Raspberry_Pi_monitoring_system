import pandas as pd
from pathlib import Path

from monitoring_system.utils.csv import *
from monitoring_system.utils.preprocess import *


def get_collected_sensors(path_to_data_folder):
    return read_csv(str(Path(path_to_data_folder).joinpath('sensors/sensing_measurements.csv')))


def augment_sensors(df):
    df = get_df_datetime(df)

    return df


def get_sensors(df):
    return get_nontime_cols(df)

