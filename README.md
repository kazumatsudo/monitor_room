# MONITOR_ROOM

Measure environmental values and record them on the monitoring server 

## Requirement

- Python 3
- Raspberry Pi 3
- sensors
    - BME280 (humidity, pressure, temperature)
    - MH-Z19 (co2)
    - TSL2561 (light)

## Usage

- Run from cron
    ```
    // run every second
    $ * * * * * for i in `seq 0 1 59`;do (sleep ${i}; python monitor_room/main.py) & done;
    ```

## Instration

1. git clone
    ```
    $ git clone xxx
    ```

1. set environment variable
    ```
    $ export MONITOR_ROOM_MACKEREL_X_API_KEY="YOUR_MACKEREL_X_API_KEY"
    $ export MONITOR_ROOM_MACKEREL_HOST_ID="YOUR_MACKEREL_HOST_ID"
    ```

1. make mackerel account

## Author

[kazumatsudo](https://kazumatsudo.jp)

## License

[MIT](./LICENSE)