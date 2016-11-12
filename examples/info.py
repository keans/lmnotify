#!/usr/bin/env python
# -*- coding: utf-8 -*-

from lmnotify import LaMetricManager


def main():
    lmn = LaMetricManager()

    # --- test cloud ---

    # get the user
    print "USER", lmn.get_user(), "\n"

    # get devices
    devices = lmn.get_devices()
    print "DEVICES", devices, "\n"

    # --- test local device ---

    # use first device to do some tests
    lmn.set_device(devices[0])

    # get all available API endpoints
    print "ENDPOINTS", lmn.get_endpoint_map(), "\n"

    # get the state of the device
    print "DEVICE", lmn.get_device_state(), "\n"

    # get display brightness
    print "DISPLAY", lmn.get_display(), "\n"

    # get the volume
    print "VOLUME", lmn.get_volume(), "\n"

    # get the bluetooth state
    print "BLUETOOTH", lmn.get_bluetooth_state(), "\n"

    # get the wifi state
    print "WIFI", lmn.get_wifi_state()


if __name__ == "__main__":
    main()
