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


def compensate_pressure(adc_pressure):
    global t_fine

    v1 = (t_fine / 2.0) - 64000.0
    v2 = (((v1 / 4.0) * (v1 / 4.0)) / 2048) * digP[5]
    v2 = v2 + ((v1 * digP[4]) * 2.0)
    v2 = (v2 / 4.0) + (digP[3] * 65536.0)
    v1 = (((digP[2] * (((v1 / 4.0) * (v1 / 4.0)) / 8192)) / 8) + ((digP[1] * v1) / 2.0)) / 262144
    v1 = ((32768 + v1) * digP[0]) / 32768

    if v1 == 0:
        return 0
    pressure = ((1048576 - adc_pressure) - (v2 / 4096)) * 3125
    if pressure < 0x80000000:
        pressure = (pressure * 2.0) / v1
    else:
        pressure = (pressure / v1) * 2
    v1 = (digP[8] * (((pressure / 8.0) * (pressure / 8.0)) / 8192.0)) / 4096
    v2 = ((pressure / 4.0) * digP[7]) / 8192.0
    pressure = pressure + ((v1 + v2 + digP[6]) / 16.0)

    return pressure / 100


def compensate_temperature(adc_temperature):
    global t_fine
    v1 = (adc_temperature / 16384.0 - digT[0] / 1024.0) * digT[1]
    v2 = (adc_temperature / 131072.0 - digT[0] / 8192.0) * (adc_temperature / 131072.0 - digT[0] / 8192.0) * digT[2]
    t_fine = v1 + v2
    temperature = t_fine / 5120.0
    return temperature


def compensate_humidity(adc_humidity):
    global t_fine
    var_h = t_fine - 76800.0
    if var_h != 0:
        var_h = (adc_humidity - (digH[3] * 64.0 + digH[4] / 16384.0 * var_h)) * (
                    digH[1] / 65536.0 * (1.0 + digH[5] / 67108864.0 * var_h * (1.0 + digH[2] / 67108864.0 * var_h)))
    else:
        return 0
    var_h = var_h * (1.0 - digH[0] * var_h / 524288.0)
    if var_h > 100.0:
        var_h = 100.0
    elif var_h < 0.0:
        var_h = 0.0

    return  var_h


def compensate_light():
    return bus.read_word_data(i2c_address_light, 0xAC)


def setup():
    osrs_t = 1  # Temperature oversampling x 1
    osrs_p = 1  # Pressure oversampling x 1
    osrs_h = 1  # Humidity oversampling x 1
    mode = 3  # Normal mode
    t_sb = 5  # Tstandby 1000ms
    filter = 0  # Filter off
    spi3w_en = 0  # 3-wire SPI Disable

    ctrl_meas_reg = (osrs_t << 5) | (osrs_p << 2) | mode
    config_reg = (t_sb << 5) | (filter << 2) | spi3w_en
    ctrl_hum_reg = osrs_h

    bus.write_byte_data(i2c_address_except_light, 0xF2, ctrl_hum_reg)
    bus.write_byte_data(i2c_address_except_light, 0xF4, ctrl_meas_reg)
    bus.write_byte_data(i2c_address_except_light, 0xF5, config_reg)
    bus.write_byte_data(i2c_address_light, 0x80, 0x03)


def get_calib_param():
    calib = []

    for i in range(0x88, 0x88 + 24):
        calib.append(bus.read_byte_data(i2c_address_except_light, i))

    calib.append(bus.read_byte_data(i2c_address_except_light, 0xA1))

    for i in range(0xE1, 0xE1 + 7):
        calib.append(bus.read_byte_data(i2c_address_except_light, i))

    digT.append((calib[1] << 8) | calib[0])
    digT.append((calib[3] << 8) | calib[2])
    digT.append((calib[5] << 8) | calib[4])
    digP.append((calib[7] << 8) | calib[6])
    digP.append((calib[9] << 8) | calib[8])
    digP.append((calib[11] << 8) | calib[10])
    digP.append((calib[13] << 8) | calib[12])
    digP.append((calib[15] << 8) | calib[14])
    digP.append((calib[17] << 8) | calib[16])
    digP.append((calib[19] << 8) | calib[18])
    digP.append((calib[21] << 8) | calib[20])
    digP.append((calib[23] << 8) | calib[22])
    digH.append(calib[24])
    digH.append((calib[26] << 8) | calib[25])
    digH.append(calib[27])
    digH.append((calib[28] << 4) | (0x0F & calib[29]))
    digH.append((calib[30] << 4) | ((calib[29] >> 4) & 0x0F))
    digH.append(calib[31])

    for i in range(1, 2):
        if digT[i] & 0x8000:
            digT[i] = (-digT[i] ^ 0xFFFF) + 1

    for i in range(1, 8):
        if digP[i] & 0x8000:
            digP[i] = (-digP[i] ^ 0xFFFF) + 1

    for i in range(0, 6):
        if digH[i] & 0x8000:
            digH[i] = (-digH[i] ^ 0xFFFF) + 1


def read_data():
    data = []
    for i in range(0xF7, 0xF7 + 8):
        data.append(bus.read_byte_data(i2c_address_except_light, i))

    pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
    temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
    hum_raw = (data[6] << 8) | data[7]

    pressure = compensate_pressure(pres_raw)
    temperature = compensate_temperature(temp_raw)
    humidity = compensate_humidity(hum_raw)
    light = compensate_light()
    ppm = measure_ppm()

    discomfort = 0.81 * temperature + 0.01 * humidity * (0.99 * temperature - 14.3) + 46.3

    return temperature, humidity, discomfort, pressure, light, ppm


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
