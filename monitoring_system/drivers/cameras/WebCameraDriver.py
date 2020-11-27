import cv2
import time

from monitoring_system.drivers.cameras.CameraDriver import CameraDriver


class WebCameraDriver(CameraDriver):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
