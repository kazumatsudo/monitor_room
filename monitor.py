# coding: utf-8

from smbus2 import SMBus
import serial
import time

import requests
import json

bus_number = 1
i2c_address_except_light = 0x76
i2c_address_light = 0x39

bus = SMBus(bus_number)

digT = []
digP = []
digH = []

t_fine = 0.0


def measure_ppm():
    ser = serial.Serial('/dev/ttyS0',
                        baudrate=9600,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        timeout=1.0)
    ser.write(b"\xff\x01\x86\x00\x00\x00\x00\x00\x79")
    str = ser.read(9)

    return str[2] * 256 + str[3]

def compensate_light():
    return bus.read_word_data(i2c_address_light, 0xAC)


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
