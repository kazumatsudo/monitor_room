# coding: utf-8

import time

import requests
import json



hostId = "3iFS5Ee4ueo"


def post_data(temprature, humidity, discomfort, pressure, light, ppm):
    now = int(time.time())

    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": "jrknLvRqfcmn8JQ8LjVNWRgp8a3hRjVEo34rMx7Hs7Sr"
    }
    payload = [
        {
            "hostId": hostId,
            "name": "custom.temprature.name",
            "time": now,
            "value": temprature
        },
        {
            "hostId": hostId,
            "name": "custom.humidity.name",
            "time": now,
            "value": humidity
        },
        {
            "hostId": hostId,
            "name": "custom.discomfort.name",
            "time": now,
            "value": discomfort
        },
        {
            "hostId": hostId,
            "name": "custom.pressure.name",
            "time": now,
            "value": pressure
        },
        {
            "hostId": hostId,
            "name": "custom.light.name",
            "time": now,
            "value": light
        },
        {
            "hostId": hostId,
            "name": "custom.ppm.name",
            "time": now,
            "value": ppm
        },
    ]

    print(requests.post("https://api.mackerelio.com/api/v0/tsdb", data=json.dumps(payload), headers=headers).text)
