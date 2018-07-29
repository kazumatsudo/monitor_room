"""BME280 - 温湿度・気圧センサモジュールキット"""


class Bme280(object):
    """BME280 - 温湿度・気圧センサモジュールキット

    http://akizukidenshi.com/catalog/g/gK-09421/

    上記センサーの値を取得するクラス
    """
    def __init__(self, bus):
        self.bus = bus
        self.i2c_address = 0x76
        self.cal = []
        self.data = []
        self.d_h = []
        self.d_p = []
        self.d_t = []
        self.t_fine = 0.0

        o_h = 1
        ctrl_hum_reg = o_h
        bus.write_byte_data(self.i2c_address, 0xF2, ctrl_hum_reg)

        o_t = 1
        o_p = 1
        mode = 3
        ctrl_meas_reg = (o_t << 5) | (o_p << 2) | mode
        bus.write_byte_data(self.i2c_address, 0xF4, ctrl_meas_reg)

        t_standby = 5
        config_reg_filter = 0  # Filter off
        spi_3_wire = 0
        config_reg = (t_standby << 5) | (config_reg_filter << 2) | spi_3_wire
        bus.write_byte_data(self.i2c_address, 0xF5, config_reg)

        self.__calibrate()

    def read_data(self):
        """センサーから取得した値を返す

        :return: object
            湿度(％), 大気圧(hPa), 温度(℃)
        """
        for i in range(0xF7, 0xF7 + 8):
            self.data.append(self.bus.read_byte_data(self.i2c_address, i))

        return {
            'humidity': self.__compensate_humidity(),
            'pressure': self.__compensate_pressure(),
            'temperature': self.__compensate_temperature()
        }

    def __calibrate(self):
        """キャリブレーションを行う

        :return: void
        """
        for i in range(0x88, 0x88 + 24):
            self.cal.append(self.bus.read_byte_data(self.i2c_address, i))

        self.cal.append(self.bus.read_byte_data(self.i2c_address, 0xA1))

        for i in range(0xE1, 0xE1 + 7):
            self.cal.append(self.bus.read_byte_data(self.i2c_address, i))

        self.d_t.append((self.cal[1] << 8) | self.cal[0])
        self.d_t.append((self.cal[3] << 8) | self.cal[2])
        self.d_t.append((self.cal[5] << 8) | self.cal[4])
        self.d_p.append((self.cal[7] << 8) | self.cal[6])
        self.d_p.append((self.cal[9] << 8) | self.cal[8])
        self.d_p.append((self.cal[11] << 8) | self.cal[10])
        self.d_p.append((self.cal[13] << 8) | self.cal[12])
        self.d_p.append((self.cal[15] << 8) | self.cal[14])
        self.d_p.append((self.cal[17] << 8) | self.cal[16])
        self.d_p.append((self.cal[19] << 8) | self.cal[18])
        self.d_p.append((self.cal[21] << 8) | self.cal[20])
        self.d_p.append((self.cal[23] << 8) | self.cal[22])
        self.d_h.append(self.cal[24])
        self.d_h.append((self.cal[26] << 8) | self.cal[25])
        self.d_h.append(self.cal[27])
        self.d_h.append((self.cal[28] << 4) | (0x0F & self.cal[29]))
        self.d_h.append((self.cal[30] << 4) | ((self.cal[29] >> 4) & 0x0F))
        self.d_h.append(self.cal[31])

        for i in range(1, 2):
            if self.d_t[i] & 0x8000:
                self.d_t[i] = (-self.d_t[i] ^ 0xFFFF) + 1

        for i in range(1, 8):
            if self.d_p[i] & 0x8000:
                self.d_p[i] = (-self.d_p[i] ^ 0xFFFF) + 1

        for i in range(0, 6):
            if self.d_h[i] & 0x8000:
                self.d_h[i] = (-self.d_h[i] ^ 0xFFFF) + 1

    def __compensate_humidity(self):
        """センサーから値を取得する

        :return: float
            湿度(％)
        """
        var_h = self.t_fine - 76800.0

        if var_h != 0:
            r_h = (self.data[6] << 8) | self.data[7]
            var_h = (r_h - (self.d_h[3] *
                            64.0 + self.d_h[4] /
                            16384.0 * var_h)) * \
                    (self.d_h[1] /
                     65536.0 * (1.0 + self.d_h[5] /
                                67108864.0 * var_h * (1.0 + self.d_h[2] /
                                                      67108864.0 * var_h)))
        else:
            return 0

        var_h = var_h * (1.0 - self.d_h[0] * var_h / 524288.0)
        if var_h > 100.0:
            var_h = 100.0
        elif var_h < 0.0:
            var_h = 0.0

        return var_h

    def __compensate_pressure(self):
        """センサーから値を取得する

        :return: float
            大気圧(hPa)
        """
        v_1 = (self.t_fine / 2.0) - 64000.0
        v_2 = pow((v_1 / 4.0), 2) * self.d_p[5] / 2048
        v_2 = v_2 + ((v_1 * self.d_p[4]) * 2.0)
        v_2 = (v_2 / 4.0) + (self.d_p[3] * 65536.0)
        v_1 = ((self.d_p[2] * pow((v_1 / 4.0), 2) / (8192 * 8)) +
               ((self.d_p[1] * v_1) / 2.0)) / 262144
        v_1 = ((32768 + v_1) * self.d_p[0]) / 32768

        if v_1 == 0:
            return 0

        r_p = (self.data[0] << 12) | (self.data[1] << 4) | (self.data[2] >> 4)
        pressure = ((1048576 - r_p) - (v_2 / 4096)) * 3125
        if pressure < 0x80000000:
            pressure = (pressure * 2.0) / v_1
        else:
            pressure = (pressure / v_1) * 2

        v_1 = self.d_p[8] * pow(pressure / 8.0, 2) / (8192.0 * 4096)
        v_2 = pressure * self.d_p[7] / (8192.0 * 4.0)
        pressure = pressure + ((v_1 + v_2 + self.d_p[6]) / 16.0)

        return pressure / 100

    def __compensate_temperature(self):
        """センサーから値を取得する

        :return: float
            温度(℃)
        """
        r_t = (self.data[3] << 12) | (self.data[4] << 4) | (self.data[5] >> 4)

        v_1 = (r_t / 16384.0 - self.d_t[0] / 1024.0) * self.d_t[1]
        v_2 = pow((r_t / 131072.0 - self.d_t[0] / 8192.0), 2) * self.d_t[2]

        self.t_fine = v_1 + v_2
        temperature = self.t_fine / 5120.0

        return temperature
