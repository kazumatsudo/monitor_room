from smbus2 import SMBus

from monitor import get_calib_param, read_data, post_data
from bme280 import setup_bme280

if __name__ == '__main__':
    bus_number = 1
    i2c_address_bme280 = 0x76

    bus = SMBus(bus_number)
    setup_bme280(bus, i2c_address_bme280)
    get_calib_param()

    temperature, humidity, discomfort, pressure, light, ppm = read_data()
    post_data(temperature, humidity, discomfort, pressure, light, ppm)
