"""
共通関数
"""


def calculate_discomfort(humidity, temperature):
    """
    不快指数を計算する

    :param humidity: int
        湿度 (％)
    :param temperature: int
        温度 (℃)
    :return: int
        不快指数 (％)
    """
    return 0.81 * temperature + 0.01 * humidity * (0.99 * temperature - 14.3) + 46.3
