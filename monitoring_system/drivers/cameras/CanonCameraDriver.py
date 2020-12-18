import time
import sh
import os
from pathlib import Path

from monitoring_system.drivers.cameras.CameraDriver import CameraDriver


class CanonCameraDriver(CameraDriver):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _setup(self):

        def get_serial_id(data):
            for s in data.split('\n'):
                if 'serial number' in s.lower():
                    s_num = s.split()[-1]
                    return s_num

        try:
            info = sh.gphoto2('--summary')
            serial_id = get_serial_id(info)

            if str(serial_id) != str(self.camera_info['device']):
                self.log.warning(
                    'Wrong SRL camera connected. Expected: ' + str(self.camera_info['device']) + '. Got: ' + str(serial_id))
        except Exception as e:
            self._send_alert('Can not init Canon camera. ' + str(e))

    def capture(self):
        for i in range(self.camera_info['focus_skip'] + 1):
            time.sleep(0.1)

            try:
                s = sh.gphoto2('--capture-image-and-download', '--force-overwrite')
                if s.exit_code != 0:
                    self.captured_image = None
                    self._send_alert('Can not capture image with SLR camera: ' + str(self.camera_info['device']))
            except Exception as e:
                self._send_alert(e)
                return

        img_path, save_path = self._get_save_path()

        Path(img_path).mkdir(parents=True, exist_ok=True)
        sh.mv(
            '/home/pi/Projects/Monitoring/capt0000.jpg',
            save_path
        )
        self.log.info('Image captured with camera: ' + str(self.camera_info['id']))

        self._save_image_data()
