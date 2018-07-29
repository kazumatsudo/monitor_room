def setup(bus, i2c_address_tsl2561):
    bus.write_byte_data(i2c_address_tsl2561, 0x80, 0x03)
