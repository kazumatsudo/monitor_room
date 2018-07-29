def setup(bus, i2c_address_bme280):
    oversampling_humidity = 1
    ctrl_hum_reg = oversampling_humidity
    bus.write_byte_data(i2c_address_bme280, 0xF2, ctrl_hum_reg)

    oversampling_temperature = 1
    oversampling_pressure = 1
    mode = 3
    ctrl_meas_reg = (oversampling_temperature << 5) | (oversampling_pressure << 2) | mode
    bus.write_byte_data(i2c_address_bme280, 0xF4, ctrl_meas_reg)

    t_standby = 5
    filter = 0  # Filter off
    spi_3_wire = 0
    config_reg = (t_standby << 5) | (filter << 2) | spi_3_wire
    bus.write_byte_data(i2c_address_bme280, 0xF5, config_reg)


def get_calibration_parameter(bus, i2c_address_bme280):
    dig_humidity = []
    dig_pressure = []
    dig_temperature = []
    calibration = []

    for i in range(0x88, 0x88 + 24):
        calibration.append(bus.read_byte_data(i2c_address_bme280, i))

    calibration.append(bus.read_byte_data(i2c_address_bme280, 0xA1))

    for i in range(0xE1, 0xE1 + 7):
        calibration.append(bus.read_byte_data(i2c_address_bme280, i))

    dig_temperature.append((calibration[1] << 8) | calibration[0])
    dig_temperature.append((calibration[3] << 8) | calibration[2])
    dig_temperature.append((calibration[5] << 8) | calibration[4])
    dig_pressure.append((calibration[7] << 8) | calibration[6])
    dig_pressure.append((calibration[9] << 8) | calibration[8])
    dig_pressure.append((calibration[11] << 8) | calibration[10])
    dig_pressure.append((calibration[13] << 8) | calibration[12])
    dig_pressure.append((calibration[15] << 8) | calibration[14])
    dig_pressure.append((calibration[17] << 8) | calibration[16])
    dig_pressure.append((calibration[19] << 8) | calibration[18])
    dig_pressure.append((calibration[21] << 8) | calibration[20])
    dig_pressure.append((calibration[23] << 8) | calibration[22])
    dig_humidity.append(calibration[24])
    dig_humidity.append((calibration[26] << 8) | calibration[25])
    dig_humidity.append(calibration[27])
    dig_humidity.append((calibration[28] << 4) | (0x0F & calibration[29]))
    dig_humidity.append((calibration[30] << 4) | ((calibration[29] >> 4) & 0x0F))
    dig_humidity.append(calibration[31])

    for i in range(1, 2):
        if dig_temperature[i] & 0x8000:
            dig_temperature[i] = (-dig_temperature[i] ^ 0xFFFF) + 1

    for i in range(1, 8):
        if dig_pressure[i] & 0x8000:
            dig_pressure[i] = (-dig_pressure[i] ^ 0xFFFF) + 1

    for i in range(0, 6):
        if dig_humidity[i] & 0x8000:
            dig_humidity[i] = (-dig_humidity[i] ^ 0xFFFF) + 1

    return dig_humidity, dig_pressure, dig_temperature


def compensate_pressure(row_pressure, dig_pressure):
    t_fine_pressure = 0.0

    v1 = (t_fine_pressure / 2.0) - 64000.0
    v2 = (((v1 / 4.0) * (v1 / 4.0)) / 2048) * dig_pressure[5]
    v2 = v2 + ((v1 * dig_pressure[4]) * 2.0)
    v2 = (v2 / 4.0) + (dig_pressure[3] * 65536.0)
    v1 = (((dig_pressure[2] * (((v1 / 4.0) * (v1 / 4.0)) / 8192)) / 8) + ((dig_pressure[1] * v1) / 2.0)) / 262144
    v1 = ((32768 + v1) * dig_pressure[0]) / 32768

    if v1 == 0:
        return 0

    pressure = ((1048576 - row_pressure) - (v2 / 4096)) * 3125
    if pressure < 0x80000000:
        pressure = (pressure * 2.0) / v1
    else:
        pressure = (pressure / v1) * 2

    v1 = (dig_pressure[8] * (((pressure / 8.0) * (pressure / 8.0)) / 8192.0)) / 4096
    v2 = ((pressure / 4.0) * dig_pressure[7]) / 8192.0
    pressure = pressure + ((v1 + v2 + dig_pressure[6]) / 16.0)

    return pressure / 100, t_fine_pressure


def compensate_temperature(raw_temperature, dig_temperature):
    v1 = (raw_temperature / 16384.0 - dig_temperature[0] / 1024.0) * dig_temperature[1]
    v2 = (raw_temperature / 131072.0 - dig_temperature[0] / 8192.0) * (raw_temperature / 131072.0 - dig_temperature[0] / 8192.0) * dig_temperature[2]

    t_fine_temperature = v1 + v2
    temperature = t_fine_temperature / 5120.0

    return temperature, t_fine_temperature


def compensate_humidity(row_humidity, dig_humidity, t_fine_temperature):
    var_h = t_fine_temperature - 76800.0

    if var_h != 0:
        var_h = (row_humidity - (dig_humidity[3] * 64.0 + dig_humidity[4] / 16384.0 * var_h)) * (
                dig_humidity[1] / 65536.0 * (1.0 + dig_humidity[5] / 67108864.0 * var_h * (1.0 + dig_humidity[2] / 67108864.0 * var_h)))
    else:
        return 0

    var_h = var_h * (1.0 - dig_humidity[0] * var_h / 524288.0)
    if var_h > 100.0:
        var_h = 100.0
    elif var_h < 0.0:
        var_h = 0.0

    return var_h


def read_data(bus, i2c_address_bme280, dig_humidity, dig_pressure, dig_temperature):
    data = []
    for i in range(0xF7, 0xF7 + 8):
        data.append(bus.read_byte_data(i2c_address_bme280, i))

    raw_pressure = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
    raw_temperature = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
    raw_humidity = (data[6] << 8) | data[7]

    pressure = compensate_pressure(raw_pressure, dig_pressure)
    temperature, t_fine_temperature = compensate_temperature(raw_temperature, dig_temperature)
    humidity = compensate_humidity(raw_humidity, dig_humidity, t_fine_temperature)

    return pressure, temperature, humidity
