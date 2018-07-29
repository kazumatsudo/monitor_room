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
    post_data_dictionary = get_parameter(bus)
    post_data(post_data_dictionary)


def setup(bus):
    setup_bme280(bus)
    setup_tsl2561(bus)


def get_parameter(bus):
    calibration_parameter = get_calibration_parameter(bus)

    data_bme280 = read_data_from_bme280(bus, calibration_parameter)
    discomfort = 0.81 * data_bme280['temperature'] + 0.01 * data_bme280['humidity'] * (0.99
                                                                                       * data_bme280['temperature']
                                                                                       - 14.3) + 46.3
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


def post_data(post_data_dictionary):
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
            "value": post_data_dictionary['temperature']
        },
        {
            "hostId": host_id,
            "name": "custom.humidity.name",
            "time": now,
            "value": post_data_dictionary['humidity']
        },
        {
            "hostId": host_id,
            "name": "custom.discomfort.name",
            "time": now,
            "value": post_data_dictionary['discomfort']
        },
        {
            "hostId": host_id,
            "name": "custom.pressure.name",
            "time": now,
            "value": post_data_dictionary['pressure']
        },
        {
            "hostId": host_id,
            "name": "custom.light.name",
            "time": now,
            "value": post_data_dictionary['light']
        },
        {
            "hostId": host_id,
            "name": "custom.ppm.name",
            "time": now,
            "value": post_data_dictionary['ppm']
        },
    ]

    post("https://api.mackerelio.com/api/v0/tsdb", data=dumps(payload), headers=headers)


if __name__ == '__main__':
    main()
