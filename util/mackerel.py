"""
監視サーバー Mackerel へデータを送信する
https://mackerel.io/ja/
"""

from json import dumps
from os import environ
from requests import post
from time import time  # pylint: disable=wrong-import-order


def post_data(data):
    """Mackerel へデータを送信する

    :param data: object
        送信するパラメータ
    :return: string
        送信結果
    """
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": environ["MONITOR_ROOM_MACKEREL_X_API_KEY"]
    }

    payload = [element for element in [
        __get_payload_element("custom.temperature.name", data['temperature']),
        __get_payload_element("custom.humidity.name", data['humidity']),
        __get_payload_element("custom.discomfort.name", data['discomfort']),
        __get_payload_element("custom.pressure.name", data['pressure']),
        __get_payload_element("custom.light.name", data['light']),
        __get_payload_element("custom.ppm.name", data['ppm'])
    ] if element is not None]

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
    if value is None:
        return None

    return {
        "hostId": environ["MONITOR_ROOM_MACKEREL_HOST_ID"],
        "name": name,
        "time": int(time()),
        "value": value
    }
