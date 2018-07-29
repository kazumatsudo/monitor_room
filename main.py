from smbus2 import SMBus

from monitor import read_data, post_data
from bme280 import setup as setup_bme280, get_calibration_parameter
from tsl2561 import setup as setup_tsl2561


def main():
    bus_number = 1
    i2c_address_bme280 = 0x76
    i2c_address_tsl2561 = 0x39

    bus = SMBus(bus_number)

    setup(bus, i2c_address_bme280, i2c_address_tsl2561)
    get_calibration_parameter(bus, i2c_address_bme280)

    temperature, humidity, discomfort, pressure, light, ppm = read_data()
    post_data(temperature, humidity, discomfort, pressure, light, ppm)


def setup(bus, i2c_address_bme280, i2c_address_tsl2561):
    setup_bme280(bus, i2c_address_bme280)
    setup_tsl2561(bus, i2c_address_tsl2561)


if __name__ == '__main__':
    main()
