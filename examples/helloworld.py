#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lmnotify import LaMetricManager, Model, SimpleFrame


def main():
    # create an instance of the LaMetricManager
    lmn = LaMetricManager()

    # get devices
    devices = lmn.get_devices()

    # use first device to do some tests
    lmn.set_device(devices[0])

    # prepare a simple frame with an icon and some text
    sf = SimpleFrame("i210", "Hello World!")

    # prepare the model that will be send as notification
    model = Model(frames=[sf])

    # send the notification the device
    lmn.send_notification(model)


if __name__ == "__main__":
    main()
