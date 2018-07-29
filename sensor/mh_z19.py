import serial


class MhZ19:
    """
    MH-Z19 - CO2二酸化炭素センサーモジュール
    https://www.amazon.co.jp/dp/B01MZI8O5E

    上記センサーの値を取得するクラス
    """
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyS0',
                            baudrate=9600,
                            bytesize=serial.EIGHTBITS,
                            parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE,
                            timeout=1.0)
        self.ser.write(b"\xff\x01\x86\x00\x00\x00\x00\x00\x79")

    def read_data(self):
        """
        センサーから取得した値を返す

        :return: float
            二酸化炭素濃度(ppm)
        """
        result = self.ser.read(9)
        return result[2] * 256 + result[3]
