from monitoring_system.drivers.sensors.Sensor import Sensor


class DigitalReadSensor(Sensor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pin = self._get_wpi_pin(self.pin)
        self._register_pins([self.pin], [])

    def get_measurements(self):
        return {
            'digital': self._digital_read(self.pin)
        }
