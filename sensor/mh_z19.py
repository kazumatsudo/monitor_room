from serial import EIGHTBITS
from serial import PARITY_NONE
from serial import Serial
from serial import STOPBITS_ONE


class MhZ19(object):
    """MH-Z19 - CO2二酸化炭素センサーモジュール

    https://www.amazon.co.jp/dp/B01MZI8O5E

    上記センサーの値を取得するクラス
    """
    def __init__(self):
        self.serial = Serial('/dev/ttyS0',
                             baudrate=9600,
                             bytesize=EIGHTBITS,
                             parity=PARITY_NONE,
                             stopbits=STOPBITS_ONE,
                             timeout=1.0)
        self.serial.write(b"\xff\x01\x86\x00\x00\x00\x00\x00\x79")

    def read_data(self):
        """センサーから取得した値を返す

        :return: float
            二酸化炭素濃度(ppm)
        """
        result = self.serial.read(9)
        return result[2] * 256 + result[3]
