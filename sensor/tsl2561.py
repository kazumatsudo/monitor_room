class Tsl2561:
    def __init__(self, bus):
        self.bus = bus
        self.i2c_address_tsl2561 = 0x39
        bus.write_byte_data(self.i2c_address_tsl2561, 0x80, 0x03)

    def read_data(self):
        return self.bus.read_word_data(self.i2c_address_tsl2561, 0xAC)
