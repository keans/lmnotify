#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lmnotify import LaMetricManager, Model, SimpleFrame

# set your LaMetric API credentials here!
CLIENT_ID = "<my_client_id>"
CLIENT_SECRET = "<my_client_secret>"


def main():
    # create an instance of the LaMetricManager
    lmn = LaMetricManager(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

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
