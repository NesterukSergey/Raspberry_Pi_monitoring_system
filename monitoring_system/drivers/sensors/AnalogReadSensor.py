from monitoring_system.drivers.sensors.Sensor import Sensor


class AnalogReadSensor(Sensor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pin = self._get_wpi_pin(self.pin)
        self._register_pins([self.pin], [])

    def get_measurements(self):
        return {
            'analog': self._analog_read(self.pin)
        }
