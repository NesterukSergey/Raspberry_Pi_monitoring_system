import cv2
import time
import numpy as np

from monitoring_system.drivers.cameras.CameraDriver import CameraDriver


class WebCameraDriver(CameraDriver):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _setup(self):
        self.cam = cv2.VideoCapture(self.camera_info['device'])

        if not self.cam.isOpened():
            error_message = 'Unable to open WebCamera: ' + str(self.camera_info['id']) + '; ' + str(self.camera_info['device'])
            self.log.error(error_message)
            self._send_alert(error_message)
            # raise RuntimeError(error_message)
            return

        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_info['width'])
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_info['height'])
        self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

        # Take some time for camera initialization
        _, _ = self.cam.read()
        time.sleep(0.1)

    def capture(self):
        for i in range(self.camera_info['focus_skip'] + 1):
            ret, image = self.cam.read()

        if self.camera_info['average'] > 0:
            images = []
            for i in range(self.camera_info['average']):
                image = self.capture_single()

                if image is not None:
                    images.append(image)

            if len(images) < 1:
                self._send_alert('Not enough images to average')
                self.captured_image = image
            else:
                images = np.array(images)
                num_images = images.shape[0]
                res = (images.sum(axis=0) / num_images).astype('uint8')
                self.captured_image = res


        else:
            self.captured_image = image

        self.cam.release()
        cv2.destroyAllWindows()
        del self.cam

        self._save_all()

    def capture_single(self):

        time.sleep(0.1)

        try:
            ret, captured_image = self.cam.read()
            if not ret:
                captured_image = None

            return captured_image

        except Exception as e:
            self._send_alert(e)
            return None
