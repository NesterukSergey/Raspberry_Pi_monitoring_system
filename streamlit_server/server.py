import time
import random
import pandas as pd
from pathlib import Path
import plotly
from PIL import Image
import streamlit as st
import sys
sys.path.append('..')

from monitoring_system.utils import *

PATH_TO_DATA_FOLDER = '../data'


def empty():
    st.header('No data found!')
    st.text('Check path to data folder or start collecting new data.')


@st.cache
def get_img(path):
    return Image.open(Path(PATH_TO_DATA_FOLDER[:-4]).joinpath(path))


@st.cache
def get_meas(df, col):
    return df[col]


if __name__ == '__main__':
    try:
        check_files = list_dirs(PATH_TO_DATA_FOLDER)  # Checking that data folder exists
        t = get_time()
        st.write('Last update time - {}:{}:{}'.format(t[1]['hour'], t[1]['minute'], t[1]['second']))

        st.sidebar.subheader('Cameras')
        show_cameras = st.sidebar.checkbox('Show cameras', value=True)
        if show_cameras:
            images = get_collected_images(PATH_TO_DATA_FOLDER)
            images = augment_images(images)
            cameras = get_cameras(images)

            for cam_num, camera in enumerate(cameras):
                show_cam_n = st.sidebar.checkbox(camera, value=cam_num == 0)

                if show_cam_n:
                    st.header('Camera: ' + str(camera))
                    camera_df = images[images['device'] == camera]

                    cam_date = st.slider(
                        'Image number',
                        min_value=1,
                        max_value=len(camera_df['datetime'].values),
                        value=len(camera_df['datetime'].values),
                        key=str(camera) + '_slider'
                    )
                    cam_date -= 1

                    st.write('Timestamp:', camera_df['datetime'].values[cam_date])
                    img_path = camera_df[camera_df['datetime'] == camera_df['datetime'].values[cam_date]]['img_path'].item()
                    img = get_img(img_path)
                    st.image(img)
                    st.write('_' * 20)


        st.sidebar.subheader('Measurements')
        show_measurements = st.sidebar.checkbox('Show measurements', value=True)
        if show_measurements:
            measurements = get_collected_sensors(PATH_TO_DATA_FOLDER)
            measurements = augment_sensors(measurements)
            sensors = get_sensors(measurements)

            for sens_num, sensor in enumerate(sensors):
                show_sens_n = st.sidebar.checkbox(sensor, value=True)
                if show_sens_n:
                    meas = get_meas(measurements, sensor)
                    st.line_chart(meas)


        st.sidebar.subheader('Miscellaneous')

        show_log = st.sidebar.checkbox('Show log')
        if show_log:
            log_files = list(map(str, list_dirs('../logs')))
            selected_log = st.sidebar.radio('Choose log file', log_files)
            st.subheader('Logs:')
            st.text(selected_log)
            st.text(read_txt(selected_log))

        show_board = st.sidebar.checkbox('Show board scheme')
        if show_board:
            board_scheme = read_txt('../board.txt')

            st.subheader('Board scheme:')
            st.text(board_scheme)

    except Exception as e:
        empty()
        raise e

    st.sidebar.button('Refresh')

# The last line is used for external server refresh
# Do not remove or modify it!!!
# 1