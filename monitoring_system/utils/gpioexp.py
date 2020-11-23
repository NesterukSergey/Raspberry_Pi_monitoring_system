# The MIT License (MIT)

import wiringpi as wp

GPIO_EXPANDER_DEFAULT_I2C_ADDRESS   = 0X2A
GPIO_EXPANDER_WHO_AM_I              = 0x00
GPIO_EXPANDER_RESET                 = 0x01
GPIO_EXPANDER_CHANGE_I2C_ADDR       = 0x02
GPIO_EXPANDER_SAVE_I2C_ADDR         = 0x03
GPIO_EXPANDER_PORT_MODE_INPUT       = 0x04
GPIO_EXPANDER_PORT_MODE_PULLUP      = 0x05
GPIO_EXPANDER_PORT_MODE_PULLDOWN    = 0x06
GPIO_EXPANDER_PORT_MODE_OUTPUT      = 0x07
GPIO_EXPANDER_DIGITAL_READ          = 0x08
GPIO_EXPANDER_DIGITAL_WRITE_HIGH    = 0x09
GPIO_EXPANDER_DIGITAL_WRITE_LOW     = 0x0A
GPIO_EXPANDER_ANALOG_WRITE          = 0x0B
GPIO_EXPANDER_ANALOG_READ           = 0x0C
GPIO_EXPANDER_PWM_FREQ              = 0x0D
GPIO_EXPANDER_ADC_SPEED             = 0x0E

INPUT          = 0
OUTPUT         = 1
INPUT_PULLUP   = 2
INPUT_PULLDOWN = 3

def getPiI2CBusNumber():
    """
    Returns the I2C bus number (/dev/i2c-#) for the Raspberry Pi being used.
    Courtesy quick2wire-python-api
    https://github.com/quick2wire/quick2wire-python-api
    """
    try:
        with open('/proc/cpuinfo','r') as f:
            for line in f:
                if line.startswith('Revision'):
                    return 1
    except:
        return 0

class gpioexp(object):
    """Troyka gpio expander."""

    def __init__(self, gpioexp_address=GPIO_EXPANDER_DEFAULT_I2C_ADDRESS):

        # Setup I2C interface for accelerometer and magnetometer.
        wp.wiringPiSetup()
        self._i2c = wp.I2C()
        self._io = self._i2c.setupInterface('/dev/i2c-' + str(getPiI2CBusNumber()), gpioexp_address)
#        self._gpioexp.write_byte(self._addr, GPIO_EXPANDER_RESET)
    def reverse_uint16(self, data):
        result = ((data & 0xff) << 8) | ((data>>8) & 0xff)
        return result

    def digitalReadPort(self):
        port = self.reverse_uint16(self._i2c.readReg16(self._io, GPIO_EXPANDER_DIGITAL_READ))
        return port

    def digitalRead(self, pin):
        mask = 0x0001 << pin
        result = 0
        if self.digitalReadPort() & mask:
            result = 1
        return result

    def digitalWritePort(self, value):
        value = self.reverse_uint16(value)
        self._i2c.writeReg16(self._io, GPIO_EXPANDER_DIGITAL_WRITE_HIGH, value)
        self._i2c.writeReg16(self._io, GPIO_EXPANDER_DIGITAL_WRITE_LOW, ~value)

    def digitalWrite(self, pin, value):
        sendData = self.reverse_uint16(0x0001<<pin)
        if value:
            self._i2c.writeReg16(self._io, GPIO_EXPANDER_DIGITAL_WRITE_HIGH, sendData)
        else:
            self._i2c.writeReg16(self._io, GPIO_EXPANDER_DIGITAL_WRITE_LOW, sendData)

    def analogRead16(self, pin):
        self._i2c.writeReg16(self._io, GPIO_EXPANDER_ANALOG_READ, pin)
        return self.reverse_uint16(self._i2c.readReg16(self._io, GPIO_EXPANDER_ANALOG_READ))

    def analogRead(self, pin):
        return self.analogRead16(pin)/4095.0

    def pwmFreq(self, freq):
        self._i2c.writeReg16(self._io, GPIO_EXPANDER_PWM_FREQ, self.reverse_uint16(freq))

    def changeAddr(self, newAddr):
        self._i2c.writeReg16(self._io, GPIO_EXPANDER_CHANGE_I2C_ADDR, newAddr)

    def saveAddr(self):
        self._i2c.write(self._io, GPIO_EXPANDER_SAVE_I2C_ADDR)

    def reset(self):
        self._i2c.write(self._io, GPIO_EXPANDER_RESET)

    def pinMode(self, pin, mode):
        sendData = self.reverse_uint16(0x0001<<pin)
        if (mode == INPUT):
            self._i2c.writeReg16(self._io, GPIO_EXPANDER_PORT_MODE_INPUT, sendData)
        if (mode == INPUT_PULLUP):
            self._i2c.writeReg16(self._io, GPIO_EXPANDER_PORT_MODE_PULLUP, sendData)
        if (mode == INPUT_PULLDOWN):
            self._i2c.writeReg16(self._io, GPIO_EXPANDER_PORT_MODE_PULLDOWN, sendData)
        if (mode == OUTPUT):
            self._i2c.writeReg16(self._io, GPIO_EXPANDER_PORT_MODE_OUTPUT, sendData)

    def analogWrite(self, pin, value):
        value = int(value*255)
        data = (pin & 0xff)|((value & 0xff)<<8)
        self._i2c.writeReg16(self._io, GPIO_EXPANDER_ANALOG_WRITE, data)
