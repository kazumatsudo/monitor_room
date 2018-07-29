from smbus2 import SMBus
from util.constants import BUS_NUMBER


def calculate_discomfort(humidity, temperature):
    return 0.81 * temperature + 0.01 * humidity * (0.99 * temperature - 14.3) + 46.3


def get_bus():
    return SMBus(BUS_NUMBER)
