#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import ConfigParser
import base64
import logging

import requests
from requests.auth import HTTPBasicAuth
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

log = logging.getLogger('requests_oauthlib')
log.setLevel(logging.DEBUG)

# default config file
CONFIG_FILE = "~/.lmconfig"


BASE_URL = "https://developer.lametric.com"

# oauth2 token url
OAUTH_TOKEN_URL = "%s/api/v2/oauth2/token" % BASE_URL

GET_USER_URL = "%s/api/v2/users/me" % BASE_URL
GET_DEVICES_URL = "%s/api/v2/users/me/devices" % BASE_URL

# notifications url
NOTIFICATION_URL = "https://%s:4343/api/v2/device/notifications"


class LaMetricNotification(object):
    """
    simple python class that allows the sending of notification
    messages to the LaMetric (https://www.lametric.com)
    """
    def __init__(self, config_file=CONFIG_FILE):
        self.load_config(os.path.expanduser(config_file))

        # create oauth2 session
        self.oauth = OAuth2Session(
            client=BackendApplicationClient(client_id=self.client_id)
        )

        # get token
        self.get_token()

    def load_config(self, config_file):
        """
        load the config from the config file or create a template
        if it is not existing yet
        """
        config = ConfigParser.ConfigParser()
        if not os.path.exists(config_file):
            # config file does not exist => create template
            config.add_section("lametric")
            config.set("lametric", "client_id", "")
            config.set("lametric", "client_secret", "")
            config.set("lametric", "redirect_url", "")
            config.set("lametric", "auth_code", "")
            with open(config_file, "wb") as configfile:
                config.write(configfile)

            sys.exit(
                "The config file '%s' does not exist. An empty "
                "template has been created. Please fill in your "
                "credentials. Abort!" % config_file
            )

        # read config file
        config.read(config_file)

        self.client_id = config.get("lametric", "client_id")
        self.client_secret = config.get("lametric", "client_secret")
        self.redirect_url = config.get("lametric", "redirect_url")
        self.auth_code = config.get("lametric", "auth_code")

    def get_token(self):
        self.token = self.oauth.fetch_token(
            token_url=OAUTH_TOKEN_URL,
            client_id=self.client_id,
            client_secret=self.client_secret
        )

    def get_user(self):

        #base64.b64encode()

        r = self.oauth.get(GET_USER_URL)
        print r.json()

    def get_devices(self):
        r = self.oauth.get(GET_DEVICES_URL)
        return r.json()

    def get_notifications(self, dev):
        r = self.oauth.get(
            NOTIFICATION_URL % dev["ipv4_internal"],
            auth=HTTPBasicAuth("dev", dev["api_key"]),
            verify=False
        )
        print r.text


    def send(self, dev, text, icon, priority="info", icon_type="info", lifetime=2000):
        assert(priority in ("info", "warning", "critical"))
        assert(priority in ("none", "info", "alert"))
        #assert(lifetime)

        data = {
            "model": {
                "frames": [
                    {
                        "icon": icon,
                        "text": text
                    }
                ]
            },
            "sound": {
               "category": "notifications",
               "id": "cat",
               "repeat":1
            },
            "icon_type": icon_type,
            "priority": priority,
            "lifetime": lifetime
        }
        r = self.oauth.post(
            NOTIFICATION_URL % dev["ipv4_internal"],
            json=data, auth=HTTPBasicAuth("dev", dev["api_key"]),
            verify=False
        )
        print r.text


def main():
    lmn = LaMetricNotification()
    user = lmn.get_user()
    devices = lmn.get_devices()
    dev = devices[0]
    lmn.get_notifications(dev)
    lmn.send(dev, "Good Night", "i120", lifetime=10000)


if __name__ == "__main__":
    main()
