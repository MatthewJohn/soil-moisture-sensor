
import time

THRESHOLDS = {
    "warn": {
        "level": "",
        "last_notification": None
    }
}

class Threshold:

    def __init__(self, label, compare):
        self._last_notification = None
        self._label = label
        self.compare = compare


def send_warning(msg):
    pass


def check_sensor(sensor, thresholds):
    val = sensor.read_u16()
    for threshold in thresholds:
        if threshold.compare(val):
            send_warning(threshold.label)
            break


adc = machine.ADC(26)

thresholds = [
    Threshold(label="Plant soil at critical dryness",
              compare=lambda x: x >= 15000),
    Threshold(label="Plant soil at warning dryness",
              compare=lambda x: x >= 13000)
]

while True:
    check_sensor(adc)
    time.sleep(60)
