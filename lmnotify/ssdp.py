#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket

# multicast address for SSDP for discovery
SSDP_MULTICAST_ADDR = ("239.255.255.250", 1900)


class SSDPDiscoveryMessage(object):
    """
    SSDP discovery message to discover devices in the network
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
        return bytes(
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
    SSDP reponse message
    """
    def __init__(self, data):
        self._parse(data)

    def _parse(self, response):
        data, addr = response
        for line in data.decode("utf-8").split("\r\n"):
            # MAKE SURE THAT WE OBTAIN OK HERE OTHERWISE SKIP
            if line not in ("", "HTTP/1.1 200 OK"):
                key, value = line.split(":", 1)
                setattr(self, key.lower(), value.strip())

    def __str__(self):
        return str(self.__dict__)


def discover(st="upnp:rootdevice", timeout=5, mx=3, retries=1):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    s.settimeout(timeout)

    msg = SSDPDiscoveryMessage(mx=mx, st=st)
    for _ in range(retries):
        print(msg)
        s.sendto(msg.bytes, SSDP_MULTICAST_ADDR)

        devices = {}
        while True:
            try:
                while True:
                    r = SSDPResponse(s.recvfrom(1024))
                    print(r)
                    devices[r.usn] = r
            except socket.timeout:
                break

    return devices


devices = discover()
print(devices)
