from json import dumps
from requests import post
from time import time


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
