#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from lmnotify import LaMetricManager, Model, SimpleFrame

# set your LaMetric API credentials here!
CLIENT_ID = "<my_client_id>"
CLIENT_SECRET = "<my_client_secret>"


def main():
    # parse the command line arguments
    parser = argparse.ArgumentParser(
        description="Send a notification to LaMetric Time"
    )
    parser.add_argument(
        "msg", metavar="MESSAGE", help="The message."
    )
    parser.add_argument(
        "--icon", "-i", default="i210", help="The icon (default: i210)."
    )
    args = parser.parse_args()

    # create an instance of the LaMetricManager
    lmn = LaMetricManager(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

    # get devices
    devices = lmn.get_devices()

    # use first device to do some tests
    lmn.set_device(devices[0])

    # obtain all registered devices from the LaMetric cloud
    devices = lmn.get_devices()

    # select the first device for interaction
    lmn.set_device(devices[0])

    # prepare a simple frame with an icon and some text
    sf = SimpleFrame(args.icon, args.msg)

    # prepare the model that will be send as notification
    model = Model(frames=[sf])

    # send the notification the device
    lmn.send_notification(model)


if __name__ == "__main__":
    main()
