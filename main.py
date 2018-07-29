from monitor import setup, get_calib_param, read_data, post_data

if __name__ == '__main__':
    setup()
    get_calib_param()

    temperature, humidity, discomfort, pressure, light, ppm = read_data()
    post_data(temperature, humidity, discomfort, pressure, light, ppm)
