from smbus2 import SMBus

from sensor.bme280 import Bme280
from sensor.mh_z19 import MhZ19
from sensor.tsl2561 import Tsl2561
from util.mackerel import post_data
from util.util import calculate_discomfort as discomfort


class Main(object):
    """メインクラス

    各センサーから取得したデータを監視サーバーに送信する
    """
    def __init__(self, bus):
        self.bme280 = Bme280(bus)
        self.mz_z19 = MhZ19()
        self.tsl2561 = Tsl2561(bus)

    def exec(self):
        """実行関数

        :return: void
        """
        print(post_data(self.__get_parameter()))

    def __get_parameter(self):
        """各センサから値を取得する

        :return: object
            不快指数(％), 湿度(％), 照度(lux), 二酸化炭素濃度(ppm), 大気圧(hPa), 温度(℃)
        """
        data = self.bme280.read_data()
        return {
            'discomfort': discomfort(data['humidity'], data['temperature']),
            'humidity': data['humidity'],
            'light': self.tsl2561.read_data(),
            'ppm': self.mz_z19.read_data(),
            'pressure': data['pressure'],
            'temperature': data['temperature']
        }


if __name__ == '__main__':
    main = Main(SMBus(1))
    main.exec()
