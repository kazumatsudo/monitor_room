from util.constants import I2C_ADDRESS_TSL2561


def setup(bus):
    bus.write_byte_data(I2C_ADDRESS_TSL2561, 0x80, 0x03)


def read_data(bus):
    return bus.read_word_data(I2C_ADDRESS_TSL2561, 0xAC)
