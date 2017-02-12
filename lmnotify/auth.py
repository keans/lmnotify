import os
from abc import ABCMeta, abstractmethod

import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from .const import CLOUD_URLS


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

    def set_credentials(self, client_id=None, client_secret=None):
        # first try to use client id and client secret from constructor
        # if not set, try to get details from environment variable
        self.client_id = (
            client_id or os.environ.get("LAMETRIC_CLIENT_ID")
        )
        self.client_secret = (
            client_secret or os.environ.get("LAMETRIC_CLIENT_SECRET")
        )

        # reset session since invalid due to credential change
        self._session = None


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
        self.set_credentials(client_id, client_secret)

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
