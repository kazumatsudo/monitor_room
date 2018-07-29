from json import dumps
from requests import post
from smbus2 import SMBus
from time import time

from sensor.bme280 import read_data as read_data_from_bme280, setup as setup_bme280, get_calibration_parameter
from sensor.mh_z19 import read_data as read_data_from_mh_z19
from sensor.tsl2561 import read_data as read_data_from_tsl2561, setup as setup_tsl2561
from util.constants import BUS_NUMBER


def main():
    bus = SMBus(BUS_NUMBER)

    setup(bus)
    post_data(get_parameter(bus))


def setup(bus):
    setup_bme280(bus)
    setup_tsl2561(bus)


def get_parameter(bus):
    dig_humidity, dig_pressure, dig_temperature = get_calibration_parameter(bus)
    pressure, temperature, humidity = read_data_from_bme280(bus, dig_humidity, dig_pressure, dig_temperature)
    discomfort = 0.81 * temperature + 0.01 * humidity * (0.99 * temperature - 14.3) + 46.3

    light = read_data_from_tsl2561(bus)
    ppm = read_data_from_mh_z19()
    return discomfort, humidity, light, ppm, pressure, temperature


def post_data(discomfort, humidity, light, ppm, pressure, temperature):
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
            "name": "custom.temperature.name",
            "time": now,
            "value": temperature
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
