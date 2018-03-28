#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import codecs
import logging

import requests
from requests.auth import HTTPBasicAuth

from .const import CLOUD_URLS, DEVICE_URLS, CONFIG_FILE, DEVICES_FILENAME
from .config import Config
from .models import AppModel
from .session import CloudSession, LocalSession
from .ssdp import SSDPManager


# disable InsecureRequestWarning: Unverified HTTPS request is being made.
requests.packages.urllib3.disable_warnings()

# prepare custom logger
log = logging.getLogger(__name__)


class LaMetricManager(object):
    """
    simple python class that allows the sending of notification
    messages to the LaMetric (https://www.lametric.com)
    """
    def __init__(
        self, client_id=None, client_secret=None,
        auto_create_config=False, auto_load_config=True,
        config_filename=CONFIG_FILE, devices_filename=DEVICES_FILENAME
    ):
        """
        initiate a LaMetricManager instance

        :param str client_id: client id obtained from the developer account of
                              the LaMetric cloud
        :param str client_secret: client secret obtained from the developer
                                  account of the LaMetric cloud
        :param bool auto_create_config: if True, an empty configuration file
                                        will be created

        :param bool auto_load_config: if True, the configuration file will be
                                      loaded, if existing i.e. client id and
                                      client secret are used from the config
        :param str config_filename: filename of the config file
        :param str devices_filename: filename where devices are locally stored
        """
        # use provided client id and secret or if not set try to use
        # the values set by the environment variables
        client_id = (
            client_id or os.environ.get("LAMETRIC_CLIENT_ID", None)
        )
        client_secret = (
            client_secret or os.environ.get("LAMETRIC_CLIENT_SECRET", None)
        )

        # get config instance
        self._config = Config(
            config_filename, auto_create_config, auto_load_config
        )

        # prepare the local session for local network communication
        self._local_session = LocalSession()

        # prepare the cloud session for communications with the LaMetric cloud
        self._cloud_session = CloudSession(
            client_id or self._config.client_id,
            client_secret or self._config.client_secret
        )

        # list of devices
        self._devices = []

        # set current device to None
        self.dev = None

        # store the result of the last call
        self.result = None

        # list of installed apps
        self.available_apps = []

        # filename where devices are stored
        self.set_devices_filename(devices_filename)

    def _exec(self, cmd, url, json_data=None):
        """
        execute a command at the device using the RESTful API

        :param str cmd: one of the REST commands, e.g. GET or POST
        :param str url: URL of the REST API the command should be applied to
        :param dict json_data: json data that should be attached to the command
        """
        assert(cmd in ("GET", "POST", "PUT", "DELETE"))
        assert(self.dev is not None)

        if json_data is None:
            json_data = {}

        # add device address to the URL
        url = url.format(self.dev["ipv4_internal"])

        # set basic authentication
        auth = HTTPBasicAuth("dev", self.dev["api_key"])

        # execute HTTP request
        res = None
        if cmd == "GET":
            res = self._local_session.session.get(
                url, auth=auth, verify=False
            )

        elif cmd == "POST":
            res = self._local_session.session.post(
                url, auth=auth, json=json_data, verify=False
            )

        elif cmd == "PUT":
            res = self._local_session.session.put(
                url, auth=auth, json=json_data, verify=False
            )

        elif cmd == "DELETE":
            res = self._local_session.session.delete(
                url, auth=auth, verify=False
            )

        if res is not None:
            # raise an exception on error
            res.raise_for_status()

        return res.json()

    def set_devices_filename(self, devices_filename):
        """
        set the filename where to store the devices locally

        :param str devices_filename: filename of the devices file
        """
        self._devices_filename = os.path.expanduser(devices_filename)

    def set_device(self, dev):
        """
        set the current device (that will be used for following API calls)

        :param dict dev: device that should be used for the API calls
                         (can be obtained via get_devices function)
        """
        log.debug("setting device to '{}'".format(dev))
        self.dev = dev
        self.set_apps_list()

    def _get_widget_id(self, package_name):
        """
        returns widget_id for given package_name does not care
        about multiple widget ids at the moment, just picks the first

        :param str package_name: package to check for
        :return: id of first widget which belongs to the given package_name
        :rtype: str
        """
        widget_id = ""
        for app in self.get_apps_list():
            if app.package == package_name:
                widget_id = list(app.widgets.keys())[0]

        return widget_id

    # ----- rest api calls on cloud ------
    def get_user(self):
        """
        get the user details via the cloud
        """
        log.debug("getting user information from LaMetric cloud...")
        _, url = CLOUD_URLS["get_user"]
        res = self._cloud_session.session.get(url)
        if res is not None:
            # raise an exception on error
            res.raise_for_status()

        return res.json()

    def get_devices(self, force_reload=False, save_devices=True):
        """
        get all devices that are linked to the user, if the local device
        file is not existing the devices will be obtained from the LaMetric
        cloud, otherwise the local device file will be read.

        :param bool force_reload: When True, devices are read again from cloud
        :param bool save_devices: When True, devices obtained from the LaMetric
                                  cloud are stored locally
        """
        if (
            (not os.path.exists(self._devices_filename)) or
            (force_reload is True)
        ):
            # -- load devices from LaMetric cloud --
            log.debug("getting devices from LaMetric cloud...")
            _, url = CLOUD_URLS["get_devices"]
            res = self._cloud_session.session.get(url)
            if res is not None:
                # raise an exception on error
                res.raise_for_status()

            # store obtained devices internally
            self._devices = res.json()
            if save_devices is True:
                # save obtained devices to the local file
                self.save_devices()

            return self._devices

        else:
            # -- load devices from local file --
            log.debug(
                "getting devices from '{}'...".format(self._devices_filename)
            )
            return self.load_devices()

    def save_devices(self):
        """
        save devices that have been obtained from LaMetric cloud
        to a local file
        """
        log.debug("saving devices to ''...".format(self._devices_filename))
        if self._devices != []:
            with codecs.open(self._devices_filename, "wb", "utf-8") as f:
                json.dump(self._devices, f)

    # ----- rest api calls locally on device ------
    def get_endpoint_map(self):
        """
        returns API version and endpoint map
        """
        log.debug("getting end points...")
        cmd, url = DEVICE_URLS["get_endpoint_map"]
        return self._exec(cmd, url)

    def discover_devices(self):
        """
        returns all LaMetric devices in the local network,
        discovered via UPNP
        """
        log.debug("discovering LaMetric devices via UPNP...")
        ssdp_manager = SSDPManager()
        return ssdp_manager.get_filtered_devices("LaMetric")

    def load_devices(self):
        """
        load stored devices from the local file
        """
        self._devices = []
        if os.path.exists(self._devices_filename):
            log.debug(
                "loading devices from '{}'...".format(self._devices_filename)
            )
            with codecs.open(self._devices_filename, "rb", "utf-8") as f:
                self._devices = json.load(f)

        return self._devices

    def get_device_state(self):
        """
        returns the full device state
        """
        log.debug("getting device state...")
        cmd, url = DEVICE_URLS["get_device_state"]
        return self._exec(cmd, url)

    def send_notification(
        self, model, priority="warning", icon_type=None, lifetime=None
    ):
        """
        sends new notification to the device

        :param Model model: an instance of the Model class that should be used
        :param str priority: the priority of the notification
                             [info, warning or critical] (default: warning)
        :param str icon_type: the icon type of the notification
                              [none, info or alert] (default: None)
        :param int lifetime: the lifetime of the notification in ms
                             (default: 2 min)
        """
        assert(priority in ("info", "warning", "critical"))
        assert(icon_type in (None, "none", "info", "alert"))
        assert((lifetime is None) or (lifetime > 0))

        log.debug("sending notification...")

        cmd, url = DEVICE_URLS["send_notification"]

        json_data = {"model": model.json(), "priority": priority}

        if icon_type is not None:
            json_data["icon_type"] = icon_type
        if lifetime is not None:
            json_data["lifetime"] = lifetime

        return self._exec(cmd, url, json_data=json_data)

    def get_notifications(self):
        """
        returns the list of all notifications in queue
        """
        log.debug("getting notifications in queue...")
        cmd, url = DEVICE_URLS["get_notifications_queue"]
        return self._exec(cmd, url)

    def get_current_notification(self):
        """
        returns the current notification (i.e. the one that is visible)
        """
        log.debug("getting visible notification...")
        cmd, url = DEVICE_URLS["get_current_notification"]
        return self._exec(cmd, url)

    def get_notification(self, notification_id):
        """
        returns a specific notification by given id

        :param str notification_id: the ID of the notification
        """
        log.debug("getting notification '{}'...".format(notification_id))
        cmd, url = DEVICE_URLS["get_notification"]
        return self._exec(cmd, url.replace(":id", notification_id))

    def remove_notification(self, notification_id):
        """
        removes the given notification from queue or dismisses it, if visible

        :param str notification_id: the ID of the notification
        """
        log.debug("removing notification '{}'...".format(notification_id))
        cmd, url = DEVICE_URLS["remove_notification"]
        return self._exec(cmd, url.replace(":id", notification_id))

    def get_display(self):
        """
        returns information about the display, including
        brightness, screensaver etc.
        """
        log.debug("getting display information...")
        cmd, url = DEVICE_URLS["get_display"]
        return self._exec(cmd, url)

    def set_display(self, brightness=100, brightness_mode="auto"):
        """
        allows to modify display state (change brightness)

        :param int brightness: display brightness [0, 100] (default: 100)
        :param str brightness_mode: the brightness mode of the display
                                    [auto, manual] (default: auto)
        """
        assert(brightness_mode in ("auto", "manual"))
        assert(brightness in range(101))

        log.debug("setting display information...")

        cmd, url = DEVICE_URLS["set_display"]
        json_data = {
            "brightness_mode": brightness_mode,
            "brightness": brightness
        }

        return self._exec(cmd, url, json_data=json_data)

    def set_screensaver(
        self, mode, is_mode_enabled, start_time=None, end_time=None,
        is_screensaver_enabled=True
    ):
        """
        set the display's screensaver mode

        :param str mode: mode of the screensaver
                         [when_dark, time_based]
        :param bool is_mode_enabled: specifies if mode is enabled or disabled
        :param str start_time: start time, only used in time_based mode
                               (format: %H:%M:%S)
        :param str end_time: end time, only used in time_based mode
                             (format: %H:%M:%S)
        :param bool is_screensaver_enabled: is overall screensaver turned on
                                            overrules mode specific settings
        """
        assert(mode in ("when_dark", "time_based"))

        log.debug("setting screensaver to '{}'...".format(mode))

        cmd, url = DEVICE_URLS["set_display"]
        json_data = {
            "screensaver": {
                "enabled": is_screensaver_enabled,
                "mode": mode,
                "mode_params": {
                    "enabled": is_mode_enabled
                },
            }
        }
        if mode == "time_based":
            # TODO: add time checks
            assert((start_time is not None) and (end_time is not None))
            json_data["screensaver"]["mode_params"]["start_time"] = start_time
            json_data["screensaver"]["mode_params"]["end_time"] = end_time

        return self._exec(cmd, url, json_data=json_data)

    def get_volume(self):
        """
        returns the current volume
        """
        log.debug("getting volumne...")
        cmd, url = DEVICE_URLS["get_volume"]
        return self._exec(cmd, url)

    def set_volume(self, volume=50):
        """
        allows to change the volume

        :param int volume: volume to be set for the current device
                           [0..100] (default: 50)
        """
        assert(volume in range(101))

        log.debug("setting volume...")

        cmd, url = DEVICE_URLS["set_volume"]
        json_data = {
            "volume": volume,
        }

        return self._exec(cmd, url, json_data=json_data)

    def get_bluetooth_state(self):
        """
        returns the bluetooth state
        """
        log.debug("getting bluetooth state...")
        cmd, url = DEVICE_URLS["get_bluetooth_state"]
        return self._exec(cmd, url)

    def set_bluetooth(self, active=None, name=None):
        """
        allows to activate/deactivate bluetooth and change the name
        """
        assert(active is not None or name is not None)

        log.debug("setting bluetooth state...")

        cmd, url = DEVICE_URLS["set_bluetooth"]
        json_data = {}
        if name is not None:
            json_data["name"] = name
        if active is not None:
            json_data["active"] = active

        return self._exec(cmd, url, json_data=json_data)

    def get_wifi_state(self):
        """
        returns the current Wi-Fi state the device is connected to
        """
        log.debug("getting wifi state...")
        cmd, url = DEVICE_URLS["get_wifi_state"]
        return self._exec(cmd, url)

    # ----- rest api calls for app control on device ------
    def set_apps_list(self):
        """
        gets installed apps and puts them into the available_apps list
        """
        log.debug("getting apps and setting them in the internal app list...")

        cmd, url = DEVICE_URLS["get_apps_list"]
        result = self._exec(cmd, url)

        self.available_apps = [
            AppModel(result[app])
            for app in result
        ]

    def get_apps_list(self):
        """
        returns the list of available apps
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
        log.debug("switching to app '{}'...".format(package))
        cmd, url = DEVICE_URLS["switch_to_app"]
        widget_id = self._get_widget_id(package)

        url = url.format('{}', package, widget_id)

        self.result = self._exec(cmd, url)

    def switch_to_next_app(self):
        """
        switches to the next app
        """
        log.debug("switching to next app...")
        cmd, url = DEVICE_URLS["switch_to_next_app"]
        self.result = self._exec(cmd, url)

    def switch_to_prev_app(self):
        """
        switches to the previous app
        """
        log.debug("switching to previous app...")
        cmd, url = DEVICE_URLS["switch_to_prev_app"]
        self.result = self._exec(cmd, url)

    def activate_widget(self, package):
        """
        activate the widget of the given package

        :param str package: name of the package
        """
        cmd, url = DEVICE_URLS["activate_widget"]

        # get widget id for the package
        widget_id = self._get_widget_id(package)
        url = url.format('{}', package, widget_id)

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
        url = url.format('{}', package, widget_id)

        json_data = {"id": action}
        if params is not None:
            json_data["params"] = params

        self.result = self._exec(cmd, url, json_data=json_data)

    def radio_play(self):
        """
        play the radio
        """
        log.debug("radio => play...")
        self._app_exec("com.lametric.radio", "radio.play")

    def radio_stop(self):
        """
        stop the radio
        """
        log.debug("radio => stop...")
        self._app_exec("com.lametric.radio", "radio.stop")

    def radio_prev(self):
        """
        previous channel of the radio
        """
        log.debug("radio => prev...")
        self._app_exec("com.lametric.radio", "radio.prev")

    def radio_next(self):
        """
        next channel of the radio
        """
        log.debug("radio => next...")
        self._app_exec("com.lametric.radio", "radio.next")

    def alarm_set(self, time, wake_with_radio=False):
        """
        set the alarm clock

        :param str time: time of the alarm (format: %H:%M:%S)
        :param bool wake_with_radio: if True, radio will be used for the alarm
                                     instead of beep sound
        """
        # TODO: check for correct time format
        log.debug("alarm => set...")
        params = {
            "enabled": True,
            "time": time,
            "wake_with_radio": wake_with_radio
        }
        self._app_exec("com.lametric.clock", "clock.alarm", params=params)

    def alarm_disable(self):
        """
        disable the alarm
        """
        log.debug("alarm => disable...")
        params = {"enabled": False}
        self._app_exec("com.lametric.clock", "clock.alarm", params=params)

    def countdown_start(self):
        """
        start the countdown
        """
        log.debug("countdown => start...")
        self._app_exec("com.lametric.countdown", "countdown.start")

    def countdown_pause(self):
        """
        pause the countdown
        """
        log.debug("countdown => pause...")
        self._app_exec("com.lametric.countdown", "countdown.pause")

    def countdown_reset(self):
        """
        reset the countdown
        """
        log.debug("countdown => reset...")
        self._app_exec("com.lametric.countdown", "countdown.reset")

    def countdown_set(self, duration, start_now):
        """
        set the countdown

        :param str duration:
        :param str start_now:
        """
        log.debug("countdown => set...")
        params = {'duration': duration, 'start_now': start_now}
        self._app_exec(
            "com.lametric.countdown", "countdown.configure", params
        )

    def stopwatch_start(self):
        """
        start the stopwatch
        """
        log.debug("stopwatch => start...")
        self._app_exec("com.lametric.stopwatch", "stopwatch.start")

    def stopwatch_pause(self):
        """
        pause the stopwatch
        """
        log.debug("stopwatch => pause...")
        self._app_exec("com.lametric.stopwatch", "stopwatch.pause")

    def stopwatch_reset(self):
        """
        reset the stopwatch
        """
        log.debug("stopwatch => reset...")
        self._app_exec("com.lametric.stopwatch", "stopwatch.reset")
