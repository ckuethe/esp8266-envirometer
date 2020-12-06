from machine import Pin, I2C, Timer  # pylint: disable=import-error
import ntptime  # pylint: disable=import-error
from mlx90614 import MLX90614  # pylint: disable=import-error
from ssd1306 import SSD1306_I2C as SSD1306  # pylint: disable=import-error
from urtc import seconds2tuple, DS3231  # pylint: disable=import-error
from bme280 import BME280  # pylint: disable=import-error
import time
import network  # pylint: disable=import-error

bus = I2C(sda=Pin(5), scl=Pin(4))

bme = BME280(i2c=bus)
mlx = MLX90614(bus)
lcd = SSD1306(128, 64, bus)
rtc = DS3231(bus)
net = network.WLAN(network.STA_IF)

if True:  # rotated
    lcd.write_cmd(0xC0)
    lcd.write_cmd(0xA0)
else:  # not rotated
    lcd.write_cmd(0xC8)
    lcd.write_cmd(0xA1)


def clocksync_cb(_=None):
    if net.active() and net.isconnected():
        try:
            ntptime.settime()
            rtc.datetime(seconds2tuple(time.time()))
        except Exception:
            pass


synctimer = Timer(-1)
synctimer.init(period=300_000, callback=clocksync_cb)


def _line(x):
    return x * 8


while True:
    t = rtc.datetime()
    lcd.fill(0)
    lcd.text("{:4d}/{:2d}/{:02d}".format(t.year, t.month, t.day), 0, _line(0))
    lcd.text("{:02d}:{:02d}:{:02d}".format(t.hour, t.minute, t.second), 0, _line(1))
    lcd.text("{:15s} {}".format(net.ifconfig()[0], " " if net.isconnected() else "!"), 0, _line(2))

    lcd.text("IR Sensor {:.1f}C".format(mlx.ambient_temp), 0, _line(4))
    lcd.text("IR Target {:.1f}C".format(mlx.object_temp), 0, _line(5))
    env = bme.values
    dp = bme.dew_point

    lcd.text("{:6s} {:.2f}C".format(env[0], dp), 0, _line(6))
    lcd.text("{:6s} {:6s}".format(env[2], env[1]), 0, _line(7))

    lcd.show()
    time.sleep(0.25)

