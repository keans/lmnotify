#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lmnotify import LaMetricManager


def main():
    # create an instance of the LaMetricManager
    lmn = LaMetricManager()

    # get devices
    devices = lmn.get_devices()

    # use first device to do some tests
    lmn.set_device(devices[0])

    # time for alarm to go off
    wake_me = "14:00"

    # set alarm and enable alarm with radio
    lmn.alarm_set(wake_me, wake_with_radio=True)

    print("Don't forget to turn the alarm off.")


if __name__ == "__main__":
    main()
