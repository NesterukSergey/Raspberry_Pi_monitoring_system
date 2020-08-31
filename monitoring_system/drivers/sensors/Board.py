from monitoring_system.utils import write_txt
from monitoring_system.drivers.sensors.sensor_factory import sensor_factory


class Board:
    def __init__(self, board_scheme, sensors, log):
        self.log = log
        self.board_scheme = board_scheme
        self.sensor_naming = sensors['naming']
        self.sensors = sensors['sensors']
        self.pins = self._name2loc()
        self.active_sensors = sensor_factory(self.sensor_naming, self.sensors, self.log)
        write_txt('board.txt', self.print_board())

    def _name2loc(self):
        pins = {}
        for sensor in self.sensors:
            if 'pin' in list(self.sensors[sensor].keys()):
                loc = str(self.sensors[sensor]['pin'])
                if loc in list(pins.keys()):
                    self.log.error('pin usage duplicates at pin: ' + loc)

                pins[loc] = {
                    'name': sensor,
                    'aux': ''
                }
            elif 'pins' in list(self.sensors[sensor].keys()):
                for pin in self.sensors[sensor]['pins']:
                    loc = str(self.sensors[sensor]['pins'][pin])
                    if loc in list(pins.keys()):
                        self.log.error('pin usage duplicates at pin: ' + loc)

                    pins[loc] = {
                        'name': sensor,
                        'aux': '(' + str(pin) + ')'
                    }
            else:
                error_message = 'Sensor must specify pin or pins: ' + str(sensor)
                self.log.error(error_message)
                raise NotImplemented(error_message)

        return pins

    def print_board(self):
        if self.board_scheme['name'] == 'rpi':
            half_len = 25
            full_len = (half_len + 4) * 2
            pad = '-' * full_len + '\n'
            fig = ''

            board_pins = list(self.pins)
            for i in range(1, 41, 2):
                left_pin = str(i)
                if left_pin in board_pins:
                    left_name = self.pins[left_pin]['name']
                    left_aux = self.pins[left_pin]['aux']
                    left = '|| {} {} '.format(left_name, left_aux).ljust(half_len, '-') + '|' + '{}|'.format(
                        left_pin).rjust(3)
                elif int(left_pin) in self.board_scheme['pow_loc']:
                    left = '|| ({}) '.format('pow').ljust(half_len, ' ') + '|' + '{}|'.format(
                        left_pin).rjust(3)
                elif int(left_pin) in self.board_scheme['gnd_loc']:
                    left = '|| ({}) '.format('gnd').ljust(half_len, ' ') + '|' + '{}|'.format(
                        left_pin).rjust(3)
                else:
                    left = '||'.ljust(half_len, ' ') + '|' + '{}|'.format(left_pin).rjust(3)

                right_pin = str(i + 1)
                if right_pin in board_pins:
                    right_name = self.pins[right_pin]['name']
                    right_aux = self.pins[right_pin]['aux']
                    right = '|' + '{}'.format(right_pin).ljust(2) + '|' + ' {} {} ||'.format(right_name,
                                                                                             right_aux).rjust(
                        half_len, '-')
                elif int(right_pin) in self.board_scheme['pow_loc']:
                    right = '|' + '{}'.format(right_pin).ljust(2) + '|' + ' ({}) ||'.format('pow').rjust(
                        half_len, ' ')
                elif int(right_pin) in self.board_scheme['gnd_loc']:
                    right = '|' + '{}'.format(right_pin).ljust(2) + '|' + ' ({}) ||'.format('gnd').rjust(
                        half_len, ' ')
                else:
                    right = '|' + '{}'.format(right_pin).ljust(2) + '|' + '||'.rjust(half_len, ' ')

                s = left + right + '\n'
                fig += s

            fig = pad + '||' + ('{:^' + str(full_len - 4) + '}').format(
                self.board_scheme['description']) + '||\n' + pad + pad + fig + pad
            return fig
        else:
            try:
                active_pins = sorted(map(int, list(self.pins.keys())))
                active_pins = map(str, active_pins)
            except:
                active_pins = sorted(list(self.pins.keys()))

            fig = self.board_scheme['description']
            max_len = 0
            for pin in active_pins:
                s = ' pin: {} -- {} {} \n'.format(pin, self.pins[pin]['name'], self.pins[pin]['aux'])
                fig += s
                max_len = max(max_len, len(s))

            pad = ('-' * max_len) + '\n'
            fig = pad + fig + pad
            return fig

    def exit(self):
        for sensor in self.active_sensors:
            self.active_sensors[sensor].exit()
