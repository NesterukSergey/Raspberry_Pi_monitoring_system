import time

from monitoring_system.drivers.sensors.Sensor import Sensor


class SwitchSensor(Sensor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__dict__.update(kwargs)
        self.pin = self._get_wpi_pin(self.pin)
        self._register_pins([], [self.pin])

        if kwargs['init'] == 'on':
            self.on()
            self.state = True
        if kwargs['init'] == 'off':
            self.off()
            self.state = False

    # def exit(self):
    #     self._exit_pin(self.pin)

    def set_state(self, val):
        self.state = bool(val)
        self._digital_write(self.pin, int(self.state))

    def on(self):
        self.set_state(1)

    def off(self):
        self.set_state(0)

    def blink(self, repeats, t):
        assert repeats > 0
        old_state = self.state

        for i in range(repeats):
            self.on()
            time.sleep(t)
            self.off()
            time.sleep(t)

        self.set_state(old_state)
