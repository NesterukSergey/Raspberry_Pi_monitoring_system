import time
from abc import ABC, abstractmethod
import wiringpi as wp
# import gpioexp
from monitoring_system.utils import gpioexp


class Sensor(ABC):
    def __init__(self, **kwargs):
        super().__init__()
        self.__dict__.update(kwargs)
        self.all_pins = []
        self.exp = gpioexp.gpioexp()

    def exit(self):
        for pin in self.all_pins:
            self._exit_pin(pin)

    def _get_wpi_pin(self, pin):
        if self.pin_naming == 'loc':
            return self._loc2bcm_wpi(pin)['wpi']
        elif self.pin_naming == 'wpi':
            return pin
        elif self.pin_naming == 'bcm':
            return self._loc2bcm_wpi(self.board_scheme['pins'][str(pin)]['loc'])['wpi']
        else:
            error_message = 'Unrecognized pin naming scheme: ' + str(self.pin_naming)
            self.log.error(error_message)
            raise NotImplemented(error_message)

    def _register_pins(self, in_pins=[], out_pins=[]):
        wp.wiringPiSetup()

        for sensor in in_pins:
            wp.pinMode(int(sensor), 0)
            self.all_pins.append(int(sensor))
            time.sleep(0.01)

        for sensor in out_pins:
            wp.pinMode(int(sensor), 1)
            self.all_pins.append(int(sensor))
            time.sleep(0.01)

    def _digital_write(self, pin, val):
        self.log.debug('Write ' + str(val) + ' to pin ' + str(pin))

        if self.board_type == '':
            wp.digitalWrite(pin, bool(int(val)))
            time.sleep(0.01)
        elif self.board_type == 'troyka_cap_ext':
            self.exp.analogWrite(pin, bool(int(val)))
            time.sleep(0.01)

    def _digital_read(self, pin):
        if self.board_type == '':
            val = wp.digitalRead(pin)
        elif self.board_type == 'troyka_cap_ext':
            val = self.exp.analogRead(pin)

        self.log.debug('Read ' + str(val) + ' from pin ' + str(pin))
        return val

    def _supports_analog(self, pin):
        if self.board_type == 'troyka_cap_ext':
            return True

        if self.board_scheme['name'] == 'rpi':
            error_message = "Board rpi doesn't support analog pins. At pin: " + str(pin)
            self.log.error(error_message)
            return False

        return False

        # TODO: add check by type of pin from board_scheme

    def _analog_write(self, pin, val):
        if self.board_type == '':
            if self._supports_analog(pin):
                wp.analogWrite(pin, val)
            else:
                self._digital_write(pin, val * 1023)
        elif self.board_type == 'troyka_cap_ext':
            self.exp.analogWrite(pin, val)

    def _analog_read(self, pin):
        if self.board_type == '':
            if self._supports_analog(pin):
                return wp.analogRead(pin)
            else:
                return self._digital_read(pin) * 1023
        elif self.board_type == 'troyka_cap_ext':
            return self.exp.analogRead(pin)

    def _loc2bcm_wpi(self, loc):
        loc = str(loc)
        d = {
            '3': {
                'bcm': 2,
                'wpi': 8
            },
            '5': {
                'bcm': 3,
                'wpi': 9
            },
            '7': {
                'bcm': 4,
                'wpi': 7
            },
            '8': {
                'bcm': 14,
                'wpi': 15
            },
            '10': {
                'bcm': 15,
                'wpi': 16
            },
            '11': {
                'bcm': 17,
                'wpi': 0
            },
            '12': {
                'bcm': 17,
                'wpi': 1
            },
            '13': {
                'bcm': 27,
                'wpi': 2
            },
            '15': {
                'bcm': 22,
                'wpi': 3
            },
            '16': {
                'bcm': 23,
                'wpi': 4
            },
            '18': {
                'bcm': 24,
                'wpi': 5
            },
            '19': {
                'bcm': 10,
                'wpi': 12
            },
            '21': {
                'bcm': 9,
                'wpi': 12
            },
            '22': {
                'bcm': 25,
                'wpi': 6
            },
            '23': {
                'bcm': 11,
                'wpi': 14
            },
            '24': {
                'bcm': 8,
                'wpi': 10
            },
            '26': {
                'bcm': 7,
                'wpi': 11
            },
            '27': {
                'bcm': 0,
                'wpi': 30
            },
            '28': {
                'bcm': 1,
                'wpi': 31
            },
            '29': {
                'bcm': 5,
                'wpi': 21
            },
            '31': {
                'bcm': 6,
                'wpi': 22
            },
            '32': {
                'bcm': 12,
                'wpi': 26
            },
            '33': {
                'bcm': 13,
                'wpi': 23
            },
            '35': {
                'bcm': 19,
                'wpi': 24
            },
            '36': {
                'bcm': 16,
                'wpi': 27
            },
            '37': {
                'bcm': 26,
                'wpi': 25
            },
            '38': {
                'bcm': 20,
                'wpi': 28
            },
            '40': {
                'bcm': 21,
                'wpi': 29
            }
        }

        if loc not in list(d.keys()):
            error_message = 'Wrong physical pin address: ' + loc
            self.log.error(error_message)
            raise UserWarning(error_message)

        return d[loc]

    def _exit_pin(self, pin):
        wp.pinMode(int(pin), 1)
        time.sleep(0.05)
        self._digital_write(pin, 0)
        time.sleep(0.05)
        wp.pinMode(int(pin), 0)
        self.log.debug('Pin ' + str(self.pin) + ' exited')
