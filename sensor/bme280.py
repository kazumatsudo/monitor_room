from util.constants import I2C_ADDRESS_BME280


class Bme280:
    def __init__(self, bus):
        self.bus = bus
        self.calibration = []
        self.data = []
        self.dig_humidity = []
        self.dig_pressure = []
        self.dig_temperature = []
        self.t_fine = 0.0

        oversampling_humidity = 1
        ctrl_hum_reg = oversampling_humidity
        bus.write_byte_data(I2C_ADDRESS_BME280, 0xF2, ctrl_hum_reg)

        oversampling_temperature = 1
        oversampling_pressure = 1
        mode = 3
        ctrl_meas_reg = (oversampling_temperature << 5) | (oversampling_pressure << 2) | mode
        bus.write_byte_data(I2C_ADDRESS_BME280, 0xF4, ctrl_meas_reg)

        t_standby = 5
        filter = 0  # Filter off
        spi_3_wire = 0
        config_reg = (t_standby << 5) | (filter << 2) | spi_3_wire
        bus.write_byte_data(I2C_ADDRESS_BME280, 0xF5, config_reg)

        self.__get_calibration_parameter()

    def read_data(self):
        for i in range(0xF7, 0xF7 + 8):
            self.data.append(self.bus.read_byte_data(I2C_ADDRESS_BME280, i))

        return {
            'humidity': self.__compensate_humidity(),
            'pressure': self.__compensate_pressure(),
            'temperature': self.__compensate_temperature()
        }

    def __get_calibration_parameter(self):
        for i in range(0x88, 0x88 + 24):
            self.calibration.append(self.bus.read_byte_data(I2C_ADDRESS_BME280, i))

        self.calibration.append(self.bus.read_byte_data(I2C_ADDRESS_BME280, 0xA1))

        for i in range(0xE1, 0xE1 + 7):
            self.calibration.append(self.bus.read_byte_data(I2C_ADDRESS_BME280, i))

        self.dig_temperature.append((self.calibration[1] << 8) | self.calibration[0])
        self.dig_temperature.append((self.calibration[3] << 8) | self.calibration[2])
        self.dig_temperature.append((self.calibration[5] << 8) | self.calibration[4])
        self.dig_pressure.append((self.calibration[7] << 8) | self.calibration[6])
        self.dig_pressure.append((self.calibration[9] << 8) | self.calibration[8])
        self.dig_pressure.append((self.calibration[11] << 8) | self.calibration[10])
        self.dig_pressure.append((self.calibration[13] << 8) | self.calibration[12])
        self.dig_pressure.append((self.calibration[15] << 8) | self.calibration[14])
        self.dig_pressure.append((self.calibration[17] << 8) | self.calibration[16])
        self.dig_pressure.append((self.calibration[19] << 8) | self.calibration[18])
        self.dig_pressure.append((self.calibration[21] << 8) | self.calibration[20])
        self.dig_pressure.append((self.calibration[23] << 8) | self.calibration[22])
        self.dig_humidity.append(self.calibration[24])
        self.dig_humidity.append((self.calibration[26] << 8) | self.calibration[25])
        self.dig_humidity.append(self.calibration[27])
        self.dig_humidity.append((self.calibration[28] << 4) | (0x0F & self.calibration[29]))
        self.dig_humidity.append((self.calibration[30] << 4) | ((self.calibration[29] >> 4) & 0x0F))
        self.dig_humidity.append(self.calibration[31])

        for i in range(1, 2):
            if self.dig_temperature[i] & 0x8000:
                self.dig_temperature[i] = (-self.dig_temperature[i] ^ 0xFFFF) + 1

        for i in range(1, 8):
            if self.dig_pressure[i] & 0x8000:
                self.dig_pressure[i] = (-self.dig_pressure[i] ^ 0xFFFF) + 1

        for i in range(0, 6):
            if self.dig_humidity[i] & 0x8000:
                self.dig_humidity[i] = (-self.dig_humidity[i] ^ 0xFFFF) + 1

    def __compensate_pressure(self):
        v1 = (self.t_fine / 2.0) - 64000.0
        v2 = (((v1 / 4.0) * (v1 / 4.0)) / 2048) * self.dig_pressure[5]
        v2 = v2 + ((v1 * self.dig_pressure[4]) * 2.0)
        v2 = (v2 / 4.0) + (self.dig_pressure[3] * 65536.0)
        v1 = (((self.dig_pressure[2] * (((v1 / 4.0) * (v1 / 4.0)) / 8192)) / 8) + ((self.dig_pressure[1] * v1) / 2.0)
              ) / 262144
        v1 = ((32768 + v1) * self.dig_pressure[0]) / 32768

        if v1 == 0:
            return 0

        row_pressure = (self.data[0] << 12) | (self.data[1] << 4) | (self.data[2] >> 4)
        pressure = ((1048576 - row_pressure) - (v2 / 4096)) * 3125
        if pressure < 0x80000000:
            pressure = (pressure * 2.0) / v1
        else:
            pressure = (pressure / v1) * 2

        v1 = (self.dig_pressure[8] * (((pressure / 8.0) * (pressure / 8.0)) / 8192.0)) / 4096
        v2 = ((pressure / 4.0) * self.dig_pressure[7]) / 8192.0
        pressure = pressure + ((v1 + v2 + self.dig_pressure[6]) / 16.0)

        return pressure / 100

    def __compensate_temperature(self):
        row_temperature = (self.data[3] << 12) | (self.data[4] << 4) | (self.data[5] >> 4)

        v1 = (row_temperature / 16384.0 - self.dig_temperature[0] / 1024.0) * self.dig_temperature[1]
        v2 = (row_temperature / 131072.0 - self.dig_temperature[0] / 8192.0) * (row_temperature / 131072.0 -
                                                                                self.dig_temperature[0] / 8192.0
                                                                                ) * self.dig_temperature[2]

        self.t_fine = v1 + v2
        temperature = self.t_fine / 5120.0

        return temperature

    def __compensate_humidity(self):
        var_h = self.t_fine - 76800.0

        if var_h != 0:
            row_humidity = (self.data[6] << 8) | self.data[7]
            var_h = (row_humidity - (self.dig_humidity[3] * 64.0 + self.dig_humidity[4] / 16384.0 * var_h)) * (
                    self.dig_humidity[1] / 65536.0 * (1.0 + self.dig_humidity[5] / 67108864.0 * var_h *
                                                      (1.0 + self.dig_humidity[2] / 67108864.0 * var_h)))
        else:
            return 0

        var_h = var_h * (1.0 - self.dig_humidity[0] * var_h / 524288.0)
        if var_h > 100.0:
            var_h = 100.0
        elif var_h < 0.0:
            var_h = 0.0

        return var_h
