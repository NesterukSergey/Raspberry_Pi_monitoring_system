from monitoring_system.drivers.sensors.DigitalReadSensor import DigitalReadSensor
from monitoring_system.drivers.sensors.SwitchSensor import SwitchSensor
from monitoring_system.drivers.sensors.Dht11Sensor import Dht11Sensor


def sensor_factory(sensor_naming, sensors, log):
    d = {}
    sensor_types = {
        'switch': SwitchSensor,
        'dht11': Dht11Sensor,
        'digital_read': DigitalReadSensor
    }

    for sensor in sensors:
        sensor_type = sensors[sensor]['type']
        if sensor_type not in list(sensor_types.keys()):
            log.error('Unrecognized sensor: ' + sensor_type)
        else:
            d[sensor] = sensor_types[sensor_type](**sensors[sensor], pin_naming=sensor_naming, log=log)

    return d
