from json import dumps
from requests import post
from smbus2 import SMBus
from time import time

from bme280 import read_data as read_data_from_bme280, setup as setup_bme280, get_calibration_parameter
from mh_z19 import read_data as read_data_from_mh_z19
from tsl2561 import read_data as read_data_from_tsl2561, setup as setup_tsl2561


def main():
    bus_number = 1
    i2c_address_bme280 = 0x76
    i2c_address_tsl2561 = 0x39

    bus = SMBus(bus_number)

    setup(bus, i2c_address_bme280, i2c_address_tsl2561)
    pressure, temperature, humidity, discomfort, light, ppm = get_parameter(bus, i2c_address_bme280)
    post_data(temperature, humidity, discomfort, pressure, light, ppm)


def setup(bus, i2c_address_bme280, i2c_address_tsl2561):
    setup_bme280(bus, i2c_address_bme280)
    setup_tsl2561(bus, i2c_address_tsl2561)


def get_parameter(bus, i2c_address_bme280):
    dig_humidity, dig_pressure, dig_temperature = get_calibration_parameter(bus, i2c_address_bme280)
    pressure, temperature, humidity = read_data_from_bme280(bus, i2c_address_bme280, dig_humidity, dig_pressure,
                                                            dig_temperature)
    discomfort = 0.81 * temperature + 0.01 * humidity * (0.99 * temperature - 14.3) + 46.3

    light = read_data_from_tsl2561()
    ppm = read_data_from_mh_z19()
    return pressure, temperature, humidity, discomfort, light, ppm


def post_data(temprature, humidity, discomfort, pressure, light, ppm):
    host_id = "3iFS5Ee4ueo"
    x_api_key = "jrknLvRqfcmn8JQ8LjVNWRgp8a3hRjVEo34rMx7Hs7Sr"
    now = int(time())

    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": x_api_key
    }

    payload = [
        {
            "hostId": host_id,
            "name": "custom.temprature.name",
            "time": now,
            "value": temprature
        },
        {
            "hostId": host_id,
            "name": "custom.humidity.name",
            "time": now,
            "value": humidity
        },
        {
            "hostId": host_id,
            "name": "custom.discomfort.name",
            "time": now,
            "value": discomfort
        },
        {
            "hostId": host_id,
            "name": "custom.pressure.name",
            "time": now,
            "value": pressure
        },
        {
            "hostId": host_id,
            "name": "custom.light.name",
            "time": now,
            "value": light
        },
        {
            "hostId": host_id,
            "name": "custom.ppm.name",
            "time": now,
            "value": ppm
        },
    ]

    post("https://api.mackerelio.com/api/v0/tsdb", data=dumps(payload), headers=headers)


if __name__ == '__main__':
    main()
