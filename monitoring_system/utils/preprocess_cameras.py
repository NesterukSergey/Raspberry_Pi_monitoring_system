import pandas as pd
from pathlib import Path

from monitoring_system.utils.csv import *
from monitoring_system.utils.preprocess import *


def get_collected_images(path_to_data_folder):
    return read_csv(str(Path(path_to_data_folder).joinpath('images/images.csv')))


def augment_images(df):
    df['device'] = df['device_type'] + '_' + df['device_id']
    df = get_df_datetime(df)

    return df


def get_cameras(df):
    return pd.unique(df['device'])
