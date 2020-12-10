import cv2
from abc import ABC, abstractmethod
from pathlib import Path

from monitoring_system.utils.csv import write_csv


class CameraDriver(ABC):
    def __init__(self, system_state='normal', **kwargs):
        super().__init__()
        self.__dict__.update(kwargs)
        self.cam = None
        self.captured_image = None
        self.system_state = system_state
        self._setup()

    @abstractmethod
    def _setup(self):
        pass

    @abstractmethod
    def capture(self):
        pass

    def _save_image(self):
        if self.captured_image is None:
            error_message = 'Unable to take photo from camera ' + str(
                self.camera_info['id']) + '; ' + str(self.camera_info['device'])
            self.log.error(error_message)
            self._send_alert(error_message)
            # raise RuntimeError(error_message)
        else:
            camera_type = str(self.camera_info['type']) + '_' + str(self.camera_info['id'])

            img_path = str(Path(self.folder).joinpath('images', camera_type, self.system_state))
            file_name = '{}_{}_{}.jpg'.format(self.datetime_prefix, camera_type, self.system_state)
            save_path = str(Path(img_path).joinpath(file_name))

            Path(img_path).mkdir(parents=True, exist_ok=True)
            cv2.imwrite(save_path, self.captured_image)
            self.log.info('Image captured with camera: ' + str(self.camera_info['id']))

            image_info = self.datetime_dict.copy()
            image_info['img_path'] = save_path
            image_info['device_type'] = self.camera_info['type']
            image_info['device'] = self.camera_info['device']
            image_info['device_id'] = self.camera_info['id']
            image_info['system_state'] = self.system_state
            write_csv(image_info, str(Path(self.folder).joinpath('images', 'images.csv')))

    def _send_alert(self, message):
        self.alert_bot.send_message(self.telegram_config['alert_chat_id'], message)
