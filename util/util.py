"""
共通関数
"""


def calculate_discomfort(h, t):
    """不快指数を計算する

    :param h: int
        湿度 (％)
    :param t: int
        温度 (℃)
    :return: int
        不快指数 (％)
    """
    return 0.81 * t + 0.01 * h * (0.99 * t - 14.3) + 46.3
