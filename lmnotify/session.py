import sys
from abc import ABCMeta, abstractmethod

import requests
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from .const import CLOUD_URLS


class Session(object):
    """
    abstract class as base for sessions
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        self._session = None

    @property
    def session(self):
        """
        property to access the session
        (will be created on first access)
        """
        if self._session is None:
            self.init_session()

        return self._session

    @abstractmethod
    def init_session(self):
        """
        will automatically be called, when the session property
        is accessed for the first time
        """
        pass

    @abstractmethod
    def is_configured(self):
        """
        must return True, when the session is ready to use
        """
        pass


class LocalSession(Session):
    """
    local session that directly communicates with the LaMetric device
    without using the Cloud-API
    (note: you need to register once using CloudAuth before the local
           authentication can be used)
    """
    def __init__(self):
        Session.__init__(self)

    def init_session(self):
        """
        init the local session
        """
        self._session = requests.Session()

    def is_configured(self):
        """
        local session is always configured
        """
        return True


class CloudSession(Session):
    """
    cloud session that uses authentication via OAuth2 with the LaMetric Cloud
    """
    def __init__(
        self, client_id=None, client_secret=None
    ):
        Session.__init__(self)

        # either use given credentials or get them from env variables
        self.set_credentials(client_id, client_secret)

    def set_credentials(self, client_id=None, client_secret=None):
        """
        set given credentials and reset the session
        """
        self._client_id = client_id
        self._client_secret = client_secret

        # make sure to reset session due to credential change
        self._session = None

    def is_configured(self):
        """
        returns True, if cloud session is configured
        """
        return self._session is not None

    def init_session(self, get_token=True):
        """
        init a new oauth2 session that is required to access the cloud

        :param bool get_token: if True, a token will be obtained, after
                               the session has been created
        """
        if (self._client_id is None) or (self._client_secret is None):
            sys.exit(
                "Please make sure to set the client id and client secret "
                "via the constructor, the environment variables or the config "
                "file; otherwise, the LaMetric cloud cannot be accessed. "
                "Abort!"
            )

        self._session = OAuth2Session(
            client=BackendApplicationClient(client_id=self._client_id)
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
            client_id=self._client_id,
            client_secret=self._client_secret
        )
