from smbus2 import SMBus

from sensor.bme280 import read_data as read_data_from_bme280, setup as setup_bme280, get_calibration_parameter
from sensor.mh_z19 import read_data as read_data_from_mh_z19
from sensor.tsl2561 import read_data as read_data_from_tsl2561, setup as setup_tsl2561
from util.constants import BUS_NUMBER
from util.mackerel import post_data
from util.util import calculate_discomfort


def main():
    bus = SMBus(BUS_NUMBER)
    setup(bus)
    post_data_dictionary = get_parameter(bus)
    post_data(post_data_dictionary)


def setup(bus):
    setup_bme280(bus)
    setup_tsl2561(bus)


def get_parameter(bus):
    calibration_parameter = get_calibration_parameter(bus)

    data_bme280 = read_data_from_bme280(bus, calibration_parameter)
    discomfort = calculate_discomfort(data_bme280['humidity'], data_bme280['temperature'])
    light = read_data_from_tsl2561(bus)
    ppm = read_data_from_mh_z19()

    return {
        'discomfort': discomfort,
        'humidity': data_bme280['humidity'],
        'light': light,
        'ppm': ppm,
        'pressure': data_bme280['pressure'],
        'temperature': data_bme280['temperature']
    }


if __name__ == '__main__':
    main()
