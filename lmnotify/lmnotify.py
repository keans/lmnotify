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

# a quick-fix for Python 2.7 to make raw_input available as input
try:
    input = raw_input
except NameError:
    pass


class LaMetricManager(object):
    """
    simple python class that allows the sending of notification
    messages to the LaMetric (https://www.lametric.com)
    """
    def __init__(
        self, client_id=None, client_secret=None, config_file=CONFIG_FILE
    ):

        # first try to use client id and client secret from constructor
        # if not set, try to get details from environment variable
        self.client_id = client_id or os.environ.get("LAMETRIC_CLIENT_ID")
        self.client_secret = client_secret or os.environ.get("LAMETRIC_CLIENT_SECRET")

        if (
            ((client_id is None) or (client_secret is None)) and
            (config_file is not None)
        ):
            # if client_id or client_secret is still not set, but config file
            # is provided try to load it
            self.load_config(os.path.expanduser(config_file))

        # just make sure that client_id and client_secret is available
        # otherwise the use of this module does not make any sense ;-)
        assert((client_id is not None) and (client_secret is not None))

        # set current device to none
        self.dev = None

        # store the result of the last call
        self.result = None

        # list of installed apps
        self.available_apps = []

        # create oauth2 session that is required to access the cloud
        self.oauth = OAuth2Session(
            client=BackendApplicationClient(client_id=self.client_id)
        )

        # get a current token
        self.get_token()

    def _exec(self, cmd, url, json_data=None):
        """
        execute a command at the device
        """
        assert(cmd in ("GET", "POST", "PUT", "DELETE"))
        assert(self.dev is not None)

        if json_data is None:
            json_data = {}

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
        load the config from the config file or ask to create a template
        if it is not existing yet
        """
        config = configparser.ConfigParser()
        if not os.path.exists(config_file):
            # config file does not exist => create template
            print("The config file '%s' does not exist. " % config_file)

            # ask if empty config file should be created
            choice = None
            while choice not in ("y", "n"):
                choice = input("Create an empty config file? [y/n] ").lower()

            if choice == "y":
                # create empty config file
                config['lametric'] = {'client_id': '', 'client_secret': ''}
                with open(config_file, "w") as f:
                    config.write(f)
                print(
                    "An empty config file has been created. Please set "
                    "the corresponding LaMetric API credentials."
                )

            sys.exit("Abort.")

        # read config file
        config.read(config_file)

        # put config details to internal variables
        self.client_id = config.get("lametric", "client_id", None)
        self.client_secret = config.get("lametric", "client_secret", None)

    def set_device(self, dev):
        """
        set the current device (that will be used for API calls)
        """
        self.dev = dev
        self.set_apps_list()

    def _get_widget_id(self, package_name):
        """
        returns widget_id for given package_name
        does not care about multiple widget ids at the moment -

        :param package_name: package to check for
        :type package_name: str
        :return: id of first widget which belongs to the given package_name
        :rtype: str
        """
        widget_id = ""
        for app in self.get_apps_list():
            if app.package == package_name:
                widget_id = list(app.widgets.keys())[0]

        return widget_id

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

        json_data = {"model": model.json(), "priority": priority}

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

    # ----- rest api calls for app control on device ------
    def set_apps_list(self):
        """
        gets installed apps and puts them into the available_apps list
        """
        cmd, url = DEVICE_URLS["get_apps_list"]
        result = self._exec(cmd, url)

        self.available_apps = [
            AppModel(result[app])
            for app in result
        ]

    def get_apps_list(self):
        """
        returns list of available apps
        """
        return self.available_apps

    def switch_to_app(self, package):
        """
        activates an app that is specified by package. Selects the first
        app it finds in the app list

        :param package: name of package/app
        :type package: str
        :return: None
        :rtype: None
        """
        cmd, url = DEVICE_URLS["switch_to_app"]
        widget_id = self._get_widget_id(package)

        url %= '%s', package, widget_id

        self.result = self._exec(cmd, url)

    def switch_to_next_app(self):
        """
        switches to next app
        """
        cmd, url = DEVICE_URLS["switch_to_next_app"]
        self.result = self._exec(cmd, url)

    def switch_to_prev_app(self):
        """
        switches to previous app
        """
        cmd, url = DEVICE_URLS["switch_to_prev_app"]
        self.result = self._exec(cmd, url)

    def _app_exec(self, package, action, params=None):
        """
        meta method for all interactions with apps

        :param package: name of package/app
        :type package: str
        :param action: the action to be executed
        :type action: str
        :param params: optional parameters for this action
        :type params: dict
        :return: None
        :rtype: None
        """

        # get list of possible commands from app.actions
        allowed_commands = []
        for app in self.get_apps_list():
            if app.package == package:
                allowed_commands = list(app.actions.keys())
                break

        # check if action is in this list
        assert(action in allowed_commands)

        cmd, url = DEVICE_URLS["do_action"]

        # get widget id for the package
        widget_id = self._get_widget_id(package)
        url %= '%s', package, widget_id

        json_data = {"id": action}
        if params is not None:
            json_data["params"] = params
        self.result = self._exec(cmd, url, json_data=json_data)

    def radio_play(self):
        self._app_exec("com.lametric.radio", "radio.play")

    def radio_stop(self):
        self._app_exec("com.lametric.radio", "radio.stop")

    def radio_prev(self):
        self._app_exec("com.lametric.radio", "radio.prev")

    def radio_next(self):
        self._app_exec("com.lametric.radio", "radio.next")

    def alarm_set(self, time, wake_with_radio=False):
        # TODO: check for correct time format
        params = {
            "enabled": True,
            "time": time,
            "wake_with_radio": wake_with_radio
        }
        self._app_exec("com.lametric.clock", "clock.alarm", params=params)

    def alarm_disable(self):
        params = {"enabled": False}
        self._app_exec("com.lametric.clock", "clock.alarm", params=params)

    def countdown_start(self):
        self._app_exec("com.lametric.countdown", "countdown.start")

    def countdown_pause(self):
        self._app_exec("com.lametric.countdown", "countdown.pause")

    def countdown_reset(self):
        self._app_exec("com.lametric.countdown", "countdown.reset")

    def countdown_set(self, duration, start_now):
        params = {'duration': duration, 'start_now': start_now}
        self._app_exec(
            "com.lametric.countdown", "countdown.configure", params
        )

    def stopwatch_start(self):
        self._app_exec("com.lametric.stopwatch", "stopwatch.start")

    def stopwatch_pause(self):
        self._app_exec("com.lametric.stopwatch", "stopwatch.pause")

    def stopwatch_reset(self):
        self._app_exec("com.lametric.stopwatch", "stopwatch.reset")
