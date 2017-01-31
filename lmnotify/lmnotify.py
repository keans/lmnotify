#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import configparser

import requests
from requests.auth import HTTPBasicAuth
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from .const import CONFIG_FILE, CLOUD_URLS, DEVICE_URLS
from .models import AppModel

# disable InsecureRequestWarning: Unverified HTTPS request is being made.
requests.packages.urllib3.disable_warnings()


class LaMetricManager(object):
    """
    simple python class that allows the sending of notification
    messages to the LaMetric (https://www.lametric.com)
    """
    def __init__(self, config_file=CONFIG_FILE):
        # set current device to none
        self.dev = None

        # list of installed apps
        self.available_apps = []

        # load the config i.e. the LaMetric API details
        self.load_config(os.path.expanduser(config_file))

        # create oauth2 session that is required to access the cloud
        self.oauth = OAuth2Session(
            client=BackendApplicationClient(client_id=self.client_id)
        )

        # get a current token
        self.get_token()

    def _exec(self, cmd, url, json_data={}):
        """
        execute a command at the device
        """
        assert(cmd in ("GET", "POST", "PUT", "DELETE"))
        assert(self.dev is not None)

        # add device address to the URL
        url = url % self.dev["ipv4_internal"]

        # set basic authentication
        auth = HTTPBasicAuth("dev", self.dev["api_key"])

        r = None
        if cmd == "GET":
            r = self.oauth.get(url, auth=auth, verify=False)

        elif cmd == "POST":
            r = self.oauth.post(url, auth=auth, json=json_data, verify=False)

        elif cmd == "PUT":
            r = self.oauth.put(url, auth=auth, json=json_data, verify=False)

        elif cmd == "DELETE":
            r = self.oauth.delete(url, auth=auth, verify=False)

        return r.json()

    def load_config(self, config_file):
        """
        load the config from the config file or create a template
        if it is not existing yet
        """
        config = configparser.ConfigParser()
        if not os.path.exists(config_file):
            # config file does not exist => create template
            config['lametric'] = {'client_id': '', 'client_secret': ''}
            with open(config_file, "w") as configfile:
                config.write(configfile)

            sys.exit(
                "The config file '%s' does not exist. An empty "
                "template has been created. Please fill in your "
                "credentials. Abort!" % config_file
            )

        # read config file
        config.read(config_file)

        # put config details to internal variables
        self.client_id = config.get("lametric", "client_id")
        self.client_secret = config.get("lametric", "client_secret")

    def set_device(self, dev):
        """
        set the current device (that will be used for API calls)
        """
        self.dev = dev
        self.get_apps_list()

    # ----- rest api calls on cloud ------
    def get_token(self):
        """
        get current oauth token
        """
        self.token = self.oauth.fetch_token(
            token_url=CLOUD_URLS["get_token"][1],
            client_id=self.client_id,
            client_secret=self.client_secret
        )

    def get_user(self):
        """
        get the user details
        """
        r = self.oauth.get(CLOUD_URLS["get_user"][1])
        return r.json()

    def get_devices(self):
        """
        get all devices that are linked to the user
        """
        r = self.oauth.get(CLOUD_URLS["get_devices"][1])
        return r.json()

    # ----- rest api calls on device ------
    def get_endpoint_map(self):
        """
        returns API version and endpoint map
        """
        cmd, url = DEVICE_URLS["get_endpoint_map"]
        return self._exec(cmd, url)

    def get_device_state(self):
        """
        returns full device state
        """
        cmd, url = DEVICE_URLS["get_device_state"]
        return self._exec(cmd, url)

    def send_notification(
        self, model, priority="warning", icon_type=None, lifetime=None
    ):
        """
        sends new notification to device
        """
        assert(priority in ("info", "warning", "critical"))
        assert(icon_type in (None, "none", "info", "alert"))
        assert(lifetime is None or (lifetime > 0))

        cmd, url = DEVICE_URLS["send_notification"]

        json_data = {"model": model.json()}
        json_data["priority"] = priority

        if icon_type is not None:
            json_data["icon_type"] = icon_type
        if lifetime is not None:
            json_data["lifetime"] = lifetime

        return self._exec(cmd, url, json_data=json_data)

    def get_notifications(self):
        """
        returns the list of notifications in queue
        """
        cmd, url = DEVICE_URLS["get_notifications_queue"]
        return self._exec(cmd, url)

    def get_current_notification(self):
        """
        returns current notification (notification that is visible)
        """
        cmd, url = DEVICE_URLS["get_current_notification"]
        return self._exec(cmd, url)

    def get_notification(self, notification_id):
        """
        returns specific notification
        """
        cmd, url = DEVICE_URLS["get_notification"]
        return self._exec(cmd, url.replace(":id", notification_id))

    def remove_notification(self, notification_id):
        """
        removes notification from queue or dismisses if it is visible
        """
        cmd, url = DEVICE_URLS["remove_notification"]
        return self._exec(cmd, url.replace(":id", notification_id))

    def get_display(self):
        """
        returns information about display, like brightness
        """
        cmd, url = DEVICE_URLS["get_display"]
        return self._exec(cmd, url)

    def set_display(self, brightness=100, brightness_mode="auto"):
        """
        allows to modify display state (change brightness)
        """
        assert(brightness_mode in ("auto", "manual"))
        assert(brightness in range(101))

        cmd, url = DEVICE_URLS["set_display"]
        json_data = {
            "brightness_mode": brightness_mode,
            "brightness": brightness
        }

        return self._exec(cmd, url, json_data=json_data)

    def get_volume(self):
        """
        returns current volume
        """
        cmd, url = DEVICE_URLS["get_volume"]
        return self._exec(cmd, url)

    def set_volume(self, volume=50):
        """
        allows to change volume
        """
        assert(volume in range(101))

        cmd, url = DEVICE_URLS["set_volume"]
        json_data = {
            "volume": volume,
        }

        return self._exec(cmd, url, json_data=json_data)

    def get_bluetooth_state(self):
        """
        returns bluetooth state
        """
        cmd, url = DEVICE_URLS["get_bluetooth_state"]
        return self._exec(cmd, url)

    def set_bluetooth(self, active=None, name=None):
        """
        allows to activate/deactivate bluetooth and change name
        """
        assert(active is not None or name is not None)

        cmd, url = DEVICE_URLS["set_bluetooth"]
        json_data = {}
        if name is not None:
            json_data["name"] = name
        if active is not None:
            json_data["active"] = active

        return self._exec(cmd, url, json_data=json_data)

    def get_wifi_state(self):
        """
        returns wi-fi state
        """
        cmd, url = DEVICE_URLS["get_wifi_state"]
        return self._exec(cmd, url)

    def get_apps_list(self):
        """
        gets installed apps and puts them into the available_apps list
        """
        cmd, url = DEVICE_URLS["get_apps_list"]
        result = self._exec(cmd, url)

        self.available_apps = []
        for app in result:
            temp_app = AppModel(app, result[app])
            self.available_apps.append(temp_app)

    def get_available_apps(self):
        """
        returns list of available apps
        """
        return self.available_apps
