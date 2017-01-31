# default config file
CONFIG_FILE = "~/.lmconfig"

# URLs that are applied to the cloud
BASE_URL = "https://developer.lametric.com"
CLOUD_URLS = {
    "get_token": ("GET", "%s/api/v2/oauth2/token" % BASE_URL),
    "get_user": ("GET", "%s/api/v2/users/me" % BASE_URL),
    "get_devices": ("GET", "%s/api/v2/users/me/devices" % BASE_URL),
}

# URLs that are applied to a device
DEVICE_URLS = {
    # Returns API version and endpoint map
    "get_endpoint_map": (
        "GET", "https://%s:4343/api/v2"
    ),
    # Returns full device state
    "get_device_state": (
        "GET", "https://%s:4343/api/v2/device"
    ),
    # Sends new notification to device
    "send_notification": (
        "POST", "https://%s:4343/api/v2/device/notifications"
    ),
    # Returns the list of notifications in queue
    "get_notifications_queue": (
        "GET", "https://%s:4343/api/v2/device/notifications"
    ),
    # Returns current notification (notification that is visible)
    "get_current_notification": (
        "GET", "https://%s:4343/api/v2/device/notifications/current"
    ),
    # Returns specific notification
    "get_notification": (
        "GET", "https://%s:4343/api/v2/device/notifications/:id"
    ),
    # Removes notification from queue or dismisses if it is visible
    "remove_notification": (
        "DELETE", "https://%s:4343/api/v2/device/notifications/:id"
    ),
    # Returns information about display, like brightness
    "get_display": (
        "GET", "https://%s:4343/api/v2/device/display"
    ),
    # Allows to modify display state (change brightness)
    "set_display": (
        "PUT", "https://%s:4343/api/v2/device/display"
    ),
    # Returns current volume
    "get_volume": (
        "GET", "https://%s:4343/api/v2/device/audio"
    ),
    # Allows to change volume
    "set_volume": (
        "PUT", "https://%s:4343/api/v2/device/audio"
    ),
    # Returns bluetooth state
    "get_bluetooth_state": (
        "GET", "https://%s:4343/api/v2/device/bluetooth"
    ),
    # Allows to activate/deactivate bluetooth and change name
    "set_bluetooth": (
        "PUT", "https://%s:4343/api/v2/device/bluetooth"
    ),
    # Returns wi-fi state
    "get_wifi_state": (
        "GET", "https://%s:4343/api/v2/device/wifi"
    ),
    # Returns list of installed apps
    "get_apps_list": (
        "GET", "https://%s:4343/api/v2/device/apps/"
    ),
    # Switch to specific app
    "switch_to_app": (
        "PUT", "https://%s:4343/api/v2/device/apps/%s/widgets/%s/activate"
    ),
    # Switch to next app
    "switch_to_next_app": (
        "PUT", "https://%s:4343/api/v2/device/apps/next"
    ),
    # Switch to previous app
    "switch_to_prev_app": (
        "PUT", "https://%s:4343/api/v2/device/apps/prev"
    ),
    # execute an action
    "do_action": (
        "POST", "https://%s:4343/api/v2/device/apps/%s/widgets/%s/action"
    )
}


# available sound IDs
SOUND_IDS = (
    "bicycle",
    "car",
    "cash",
    "cat",
    "dog",
    "dog2",
    "energy",
    "knock-knock",
    "letter_email",
    "lose1",
    "lose2",
    "negative1",
    "negative2",
    "negative3",
    "negative4",
    "negative5",
    "notification",
    "notification2",
    "notification3",
    "notification4",
    "open_door",
    "positive1",
    "positive2",
    "positive3",
    "positive4",
    "positive5",
    "positive6",
    "statistic",
    "thunder",
    "water1",
    "water2",
    "win",
    "win2",
    "wind",
    "wind_short"
)

# available (sound) alarm IDs
ALARM_IDS = (
    "alarm1",
    "alarm2",
    "alarm3",
    "alarm4",
    "alarm5",
    "alarm6",
    "alarm7",
    "alarm8",
    "alarm9",
    "alarm10",
    "alarm11",
    "alarm12",
    "alarm13"
)

# available properties of an app

AVAILABLE_APP_PROPERTIES = [
    'package',
    'vendor',
    'version',
    'version_code',
    'widgets',
    'actions'
]
