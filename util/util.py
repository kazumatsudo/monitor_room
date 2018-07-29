"""
共通関数
"""


def calculate_discomfort(x_h, x_t):
    """不快指数を計算する

    :param x_h: int
        湿度 (％)
    :param x_t: int
        温度 (℃)
    :return: int
        不快指数 (％)
    """
    return 0.81 * x_t + 0.01 * x_h * (0.99 * x_t - 14.3) + 46.3
