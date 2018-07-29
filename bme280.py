def setup_bme280(bus, i2c_address_bme280):
    osrs_t = 1  # Temperature oversampling x 1
    osrs_p = 1  # Pressure oversampling x 1
    osrs_h = 1  # Humidity oversampling x 1
    mode = 3  # Normal mode
    t_sb = 5  # Tstandby 1000ms
    filter = 0  # Filter off
    spi3w_en = 0  # 3-wire SPI Disable

    ctrl_meas_reg = (osrs_t << 5) | (osrs_p << 2) | mode
    config_reg = (t_sb << 5) | (filter << 2) | spi3w_en
    ctrl_hum_reg = osrs_h

    bus.write_byte_data(i2c_address_bme280, 0xF2, ctrl_hum_reg)
    bus.write_byte_data(i2c_address_bme280, 0xF4, ctrl_meas_reg)
    bus.write_byte_data(i2c_address_bme280, 0xF5, config_reg)
