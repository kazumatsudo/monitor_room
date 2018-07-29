from sensor.bme280 import Bme280
from sensor.mh_z19 import MhZ19
from sensor.tsl2561 import Tsl2561
from util.mackerel import post_data
from util.util import calculate_discomfort, get_bus


class Main:
    def __init__(self):
        self.bus = get_bus()

        self.bme280 = Bme280(self.bus)
        self.mz_z19 = MhZ19()
        self.tsl2561 = Tsl2561(self.bus)

    def exec(self):
        post_data(self.__get_parameter())

    def __get_parameter(self):
        data_bme280 = self.bme280.read_data()
        return {
            'discomfort': calculate_discomfort(data_bme280['humidity'], data_bme280['temperature']),
            'humidity': data_bme280['humidity'],
            'light': self.tsl2561.read_data(),
            'ppm': self.mz_z19.read_data(),
            'pressure': data_bme280['pressure'],
            'temperature': data_bme280['temperature']
        }


if __name__ == '__main__':
    main = Main()
    main.exec()
