import serial


class MhZ19:
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyS0',
                            baudrate=9600,
                            bytesize=serial.EIGHTBITS,
                            parity=serial.PARITY_NONE,
                            stopbits=serial.STOPBITS_ONE,
                            timeout=1.0)
        self.ser.write(b"\xff\x01\x86\x00\x00\x00\x00\x00\x79")

    def read_data(self):
        result = self.ser.read(9)
        return result[2] * 256 + result[3]
