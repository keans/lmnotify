#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import socket
import xml.etree.ElementTree as ET

import requests

#  SSDP multicast address for device discovery
SSDP_MULTICAST_ADDR = ("239.255.255.250", 1900)


class SSDPDiscoveryMessage(object):
    """
    SSDP discovery message to discover devices on the network
    """
    def __init__(
        self, host=SSDP_MULTICAST_ADDR[0], port=SSDP_MULTICAST_ADDR[1],
        mx=3, st="ssdp:all"
    ):
        self.host = host
        self.port = port
        self.mx = mx
        self.st = st

    @property
    def bytes(self):
        """
        returns the message as bytes so that it can be sent
        through the network via UDP
        """
        return bytearray(
            "\r\n".join([
                "M-SEARCH * HTTP/1.1",
                "HOST: {host}:{port}",
                'MAN: "ssdp:discover"',
                "MX: {mx}",
                "ST: {st}",
                "", ""
            ]).format(**self.__dict__),
            "utf-8"
        )

    def __str__(self):
        return self.bytes.decode("utf-8")


class SSDPResponse(object):
    """
    SSDP reponse message that parses the result of
    an SSDP discovery message and set it as properties
    """
    def __init__(self, data):
        self._parse(data)

    def _parse(self, response):
        # get data and IP address of response
        data, addr = response

        # decode the data and split it into lines
        lines = data.decode("utf-8").strip().split("\r\n")

        if lines.pop(0) == "HTTP/1.1 200 OK":
            # if request was successful, parse lines and set attributes
            for line in lines:
                key, value = line.split(":", 1)
                setattr(self, key.lower(), value.strip())

    def __str__(self):
        return str(self.__dict__)


class SSDPManager(object):
    """
    SSDP Manager to discover UPNP devices in the network
    """

    def discover_upnp_devices(
        self, st="upnp:rootdevice", timeout=2, mx=1, retries=1
    ):
        """
        sends an SSDP discovery packet to the network and collects
        the devices that replies to it. A dictionary is returned
        using the devices unique usn as key
        """
        # prepare UDP socket to transfer the SSDP packets
        s = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
        )
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        s.settimeout(timeout)

        # prepare SSDP discover message
        msg = SSDPDiscoveryMessage(mx=mx, st=st)

        # try to get devices with multiple retries in case of failure
        devices = {}
        for _ in range(retries):
            # send SSDP discovery message
            s.sendto(msg.bytes, SSDP_MULTICAST_ADDR)

            devices = {}
            try:
                while True:
                    # parse response and store it in dict
                    r = SSDPResponse(s.recvfrom(1024))
                    devices[r.usn] = r

            except socket.timeout:
                break

        return devices

    def get_filtered_devices(
        self, model_name, device_types="upnp:rootdevice", timeout=2
    ):
        """
        returns a dict of devices that contain the given model name
        """

        # get list of all UPNP devices in the network
        upnp_devices = self.discover_upnp_devices(st=device_types)

        # go through all UPNP devices and filter wanted devices
        filtered_devices = collections.defaultdict(dict)
        for dev in upnp_devices.values():
            try:
                # download XML file with information about the device
                # from the device's location
                r = requests.get(dev.location, timeout=timeout)

                if r.status_code == requests.codes.ok:
                    # parse returned XML
                    root = ET.fromstring(r.text)

                    # add shortcut for XML namespace to access sub nodes
                    ns = {"upnp": "urn:schemas-upnp-org:device-1-0"}

                    # get device element
                    device = root.find("upnp:device", ns)

                    if model_name in device.find(
                        "upnp:modelName", ns
                    ).text:
                        # model name is wanted => add to list

                        # get unique UDN of the device that is used as key
                        udn = device.find("upnp:UDN", ns).text

                        # add url base
                        url_base = root.find("upnp:URLBase", ns)
                        if url_base is not None:
                            filtered_devices[udn][
                                "URLBase"
                            ] = url_base.text

                        # add interesting device attributes and
                        # use unique UDN as key
                        for attr in (
                            "deviceType", "friendlyName", "manufacturer",
                            "manufacturerURL", "modelDescription",
                            "modelName", "modelNumber"
                        ):
                            el = device.find("upnp:%s" % attr, ns)
                            if el is not None:
                                filtered_devices[udn][
                                    attr
                                ] = el.text.strip()

            except requests.exceptions.ConnectTimeout:
                # just skip devices that are not replying in time
                print("Timeout for '%s'. Skipping." % dev.location)

        return filtered_devices


if __name__ == "__main__":
    # small test to obtain all LaMetric devices
    ssdp_manager = SSDPManager()
    devices = ssdp_manager.get_filtered_devices("LaMetric")
    import pprint
    pprint.pprint(devices)
