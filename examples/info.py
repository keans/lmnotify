#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint

from lmnotify import LaMetricManager


def main():
    # create an instance of the LaMetricManager
    lmn = LaMetricManager()

    # --- test cloud ---

    # get the user
    print("USER\n")
    pprint(lmn.get_user(), indent=2)

    # get devices

    devices = lmn.get_devices()
    print("\nDEVICES\n")
    pprint(devices, indent=2)

    # --- test local device ---

    # use first device to do some tests
    lmn.set_device(devices[0])

    # get all available API endpoints
    print("\nENDPOINTS\n")
    pprint(lmn.get_endpoint_map(), indent=2)

    # get the state of the device
    print("\nDEVICE\n")
    pprint(lmn.get_device_state(), indent=2)

    # get display brightness
    print("\nDISPLAY\n")
    pprint(lmn.get_display(), indent=2)

    # get the volume
    print("\nVOLUME\n")
    pprint(lmn.get_volume(), indent=2)

    # get the bluetooth state
    print("\nBLUETOOTH\n")
    pprint(lmn.get_bluetooth_state(), indent=2)

    # get the wifi state
    print("\nWIFI\n")
    pprint(lmn.get_wifi_state(), indent=2)


if __name__ == "__main__":
    main()
