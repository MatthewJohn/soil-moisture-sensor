
import time
import ujson
import network

from urequest import request


with open("config.json", "r") as fh:
    config = ujson.load(fh)


def connect_to_wifi():
    # Connect to Wifi network
    print("Starting Wifi")
    for _ in range(5):
        # Connect to wifi
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        print("Attempting to connect to:", config.get("wifi_ssid"))
        wlan.connect(config.get("wifi_ssid"), config.get("wifi_password"))

        connect_timeout = 5
        while wlan.isconnected() == False and connect_timeout > 0:
            print('Waiting for connection...')
            time.sleep(1)
            connect_timeout -= 1

        # If connected break from setup
        if wlan.isconnected():
            print("Successfully connected to Wifi")
            return wlan
        else:
            print("Failed to connect to wifi network")
            # Disconnect from current network
            wlan.disconnect()
    else:
        print("Could not find WIFI network")

    return None


def send_notification(msg):
    wlan = connect_to_wifi()
    if wlan:
        print("Sending notification")
        # Send message
        request("POST", config.get("discord_webhook"), json={"content": msg})
        print("Disconnecting from wifi")
        wlan.disconnect()
        return True
    return False


class Threshold:

    def __init__(self, label, compare, interval_mins):
        self._last_notification = None
        self._interval_mins = interval_mins
        self._label = label
        self.compare = compare
        
    def send_notification(self):
        if (self._last_notification is not None and
              (self._last_notification + (self._interval_mins * 60 * 1000)) > time.ticks_ms()):
            print("Last notification too recent")
            return

        if send_notification(self._label):
            self._last_notification = time.ticks_ms()


def check_sensor(sensor, thresholds):
    print("Checking sensor")
    sum_val = 0
    for _ in range(3):
        val = sensor.read_u16()
        print("Read value: ", val)
        sum_val += val
        time.sleep(0.5)
    val = sum_val / 3
    print("Got average value: ", val)
    for threshold in thresholds:
        if threshold.compare(val):
            print("Breaching threshold")
            threshold.send_notification()
            break


adc = machine.ADC(26)

thresholds = [
    Threshold(label="Plant soil at critical dryness",
              compare=lambda x: x >= 14000,
              interval_mins=120),
    Threshold(label="Plant soil at warning dryness",
              compare=lambda x: x >= 13500,
              interval_mins=12*60),
]

while True:
    check_sensor(adc, thresholds)
    time.sleep(60)

