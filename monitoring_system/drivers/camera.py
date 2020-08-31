from pathlib import Path
import time
import cv2

from monitoring_system.utils.csv import write_csv


class RGBCameraDriver:
    def __init__(self, camera_info, folder, log, datetime_prefix, datetime_dict):
        self.camera_info = camera_info
        self.cam = None
        self.captured_image = None
        self.folder = folder
        self.log = log
        self.datetime_prefix, self.datetime_dict = datetime_prefix, datetime_dict
        self._setup()

    def _setup(self):
        self.cam = cv2.VideoCapture(self.camera_info['device'])

        if not self.cam.isOpened():
            error_message = 'Unable to open camera: ' + str(self.camera_info['id']) + '; ' + str(self.camera_info['device'])
            self.log.error(error_message)
            raise RuntimeError(error_message)

        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_info['width'])
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_info['height'])

        # Take some time for camera initialization
        time.sleep(0.1)

    def capture(self):
        for i in range(self.camera_info['focus_skip'] + 1):
            ret, self.captured_image = self.cam.read()
            if not ret:
                self.captured_image = None

        self.cam.release()
        self._save_image()

    def _save_image(self):
        if self.captured_image is None:
            error_message = 'Unable to take photo from camera ' + str(
                self.camera_info['id']) + '; ' + str(self.camera_info['device'])
            self.log.error(error_message)
            raise RuntimeError(error_message)
        else:
            camera_type = str(self.camera_info['type']) + '_' + str(self.camera_info['id'])
            img_path = str(
                Path(self.folder).joinpath(
                    'images', camera_type, self.datetime_prefix + '_' + camera_type + '.png')
            )
            cv2.imwrite(img_path, self.captured_image)
            self.log.info('Image captured with camera: ' + str(self.camera_info['id']))

            image_info = self.datetime_dict.copy()
            image_info['img_path'] = img_path
            image_info['device_type'] = self.camera_info['type']
            image_info['device'] = self.camera_info['device']
            image_info['device_id'] = self.camera_info['id']
            write_csv(image_info, str(Path(self.folder).joinpath('images', 'images.csv')))
