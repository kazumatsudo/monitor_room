class Tsl2561(object):
    """TSL2561 - 照度センサーモジュール

    http://akizukidenshi.com/catalog/g/gM-08219/

    上記センサーの値を取得するクラス
    """
    def __init__(self, bus):
        self.bus = bus
        self.i2c_address = 0x39
        bus.write_byte_data(self.i2c_address, 0x80, 0x03)

    def read_data(self):
        """センサーから取得した値を返す

        :return: float
            照度(lux)
        """
        return self.bus.read_word_data(self.i2c_address, 0xAC)
