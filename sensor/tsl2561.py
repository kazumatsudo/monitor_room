from util.constants import I2C_ADDRESS_TSL2561


class Tsl2561:
    def __init__(self, bus):
        self.bus = bus
        bus.write_byte_data(I2C_ADDRESS_TSL2561, 0x80, 0x03)

    def read_data(self):
        return self.bus.read_word_data(I2C_ADDRESS_TSL2561, 0xAC)
