"""
監視サーバー Mackerel へデータを送信する
https://mackerel.io/ja/
"""

from json import dumps
from requests import post
from time import time


def post_data(data):
    """Mackerel へデータを送信する

    :param data: object
        送信するパラメータ
    :return: string
        送信結果
    """
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": "jrknLvRqfcmn8JQ8LjVNWRgp8a3hRjVEo34rMx7Hs7Sr"
    }

    payload = [
        __get_payload_element("custom.temperature.name", data['temperature']),
        __get_payload_element("custom.humidity.name", data['humidity']),
        __get_payload_element("custom.discomfort.name", data['discomfort']),
        __get_payload_element("custom.pressure.name", data['pressure']),
        __get_payload_element("custom.light.name", data['light']),
        __get_payload_element("custom.ppm.name", data['ppm'])
    ]

    return post("https://api.mackerelio.com/api/v0/tsdb",
                data=dumps(payload),
                headers=headers).text


def __get_payload_element(name, value):
    """Mackerel への送信用パラメータの要素を返す

    :param name: string
        Mackerel での表示名
    :param value: float
        センサーが取得した値
    :return: object
        Mackerel への送信用パラメータの要素
    """
    return {
        "hostId": "3iFS5Ee4ueo",
        "name": name,
        "time": int(time()),
        "value": value
    }
