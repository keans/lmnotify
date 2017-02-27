import os
import sys
from abc import ABCMeta, abstractmethod

# import config parser python2 and python3
try:
    import ConfigParser as configparser
except ImportError:
    import configparser

import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from .const import CLOUD_URLS, CONFIG_FILE


class Auth(object):
    """
    abstract class as base for authentication
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        self._session = None

    @property
    def session(self):
        if self._session is None:
            self.init_session()

        return self._session

    @abstractmethod
    def init_session(self):
        pass


class LocalAuth(Auth):
    """
    local authentication class to communicate with the LaMetric device
    without using the Cloud-API
    (note: you need to register once using CloudAuth before the local
           authentication can be used)
    """
    def __init__(self):
        Auth.__init__(self)

    def init_session(self):
        self._session = requests.Session()


class CloudAuth(Auth):
    """
    authentication via OAuth2 using the LaMetric cloud
    """
    def __init__(self, client_id=None, client_secret=None):
        Auth.__init__(self)

        # either use given credentials or get them from env variables
        self.set_credentials(client_id, client_secret)

    def set_credentials(self, client_id=None, client_secret=None):
        """
        set given credentials, if not set try to get credentials from
        environment variables
        """
        # first try to use client id and client secret from constructor
        # if not set, try to get details from environment variable
        self.client_id = (
            client_id or os.environ.get("LAMETRIC_CLIENT_ID")
        )
        self.client_secret = (
            client_secret or os.environ.get("LAMETRIC_CLIENT_SECRET")
        )

        # make sure to reset session due to credential change
        self._session = None

    def load_config(self, config_file=CONFIG_FILE, create=True):
        """
        load the credentials from the config file
        """
        # expand user directory of config file
        config_file = os.path.expanduser(config_file)

        # prepare config parser
        config = configparser.ConfigParser()
        if not os.path.exists(config_file):
            # ---  config file not found ---
            if create is True:
                # create config file based on template
                config.add_section("lametric")
                config.set("lametric", "client_id", "")
                config.set("lametric", "client_secret", "")
                with open(config_file, "w") as f:
                    config.write(f)
                sys.exit(
                    "An empty config file '%s' has been created. Please set "
                    "the corresponding LaMetric API credentials." % config_file
                )

            else:
                sys.exit(
                    "Could not open config file '%s'. Abort!" % config_file
                )

        else:
            # ---  read config file ---

            # read config file
            config.read(config_file)

            # put config details to internal variables
            self.client_id = config.get("lametric", "client_id", None)
            self.client_secret = config.get("lametric", "client_secret", None)

            # make sure to reset session due to credential change
            self._session = None

    def init_session(self, get_token=True):
        # create oauth2 session that is required to access the cloud
        self._session = OAuth2Session(
            client=BackendApplicationClient(client_id=self.client_id)
        )

        if get_token is True:
            # get oauth token
            self.get_token()

    def get_token(self):
        """
        get current oauth token
        """
        self.token = self._session.fetch_token(
            token_url=CLOUD_URLS["get_token"][1],
            client_id=self.client_id,
            client_secret=self.client_secret
        )
