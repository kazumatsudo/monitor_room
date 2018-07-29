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
    dig_temperature = []
    dig_pressure = []
    dig_humidity = []
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
