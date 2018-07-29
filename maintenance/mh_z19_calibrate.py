"""MH-Z19 - キャリブレーション"""

from serial import EIGHTBITS  # pylint: disable=no-name-in-module
from serial import PARITY_NONE  # pylint: disable=no-name-in-module
from serial import Serial  # pylint: disable=no-name-in-module
from serial import STOPBITS_ONE  # pylint: disable=no-name-in-module

Serial('/dev/ttyS0',
       baudrate=9600,
       bytesize=EIGHTBITS,
       parity=PARITY_NONE,
       stopbits=STOPBITS_ONE,
       timeout=1.0).write(b"\xff\x01\x87\x00\x00\x00\x00\x00\x78")
print("calibration zero point done.")
