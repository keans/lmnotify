import os
import sys

# import config parser python2 and python3
try:
    import ConfigParser as configparser
except ImportError:
    import configparser


class Config(object):
    """
    configuration object
    """
    def __init__(
        self, config_file, auto_create=True, auto_load=True
    ):
        """
        initiate the config class

        :param str config_file: filename of the config file
        :param bool auto_create: if True, an empty config file will be created
                                 if it is not existing yet
        :param bool auto_load: if True, the config will be loaded directly
                               on the initiation of the config class
        """
        # expand user directory of config file
        self._filename = os.path.expanduser(config_file)

        # prepare config parser
        self.config = configparser.ConfigParser()

        if auto_create is True:
            # create an empty configuration file
            self.create()

        if auto_load is True:
            # load existing config on start
            self.load()

    @property
    def client_id(self):
        """
        returns the client ID from the config or None, if not existing
        """
        if not self.config.has_option("lametric", "client_id"):
            return None

        return self.config.get("lametric", "client_id")

    @property
    def client_secret(self):
        """
        return the client secret from the config or None, if not existing
        """
        if not self.config.has_option("lametric", "client_secret"):
            return None

        return self.config.get("lametric", "client_secret")

    def create(self):
        """
        creates an empty configuration file
        """
        if not self.exists():
            # create new empyt config file based on template
            self.config.add_section("lametric")
            self.config.set("lametric", "client_id", "")
            self.config.set("lametric", "client_secret", "")

            # save new config
            self.save()

            # stop here, so user can set his config
            sys.exit(
                "An empty config file '{}' has been created. Please set "
                "the corresponding LaMetric API credentials.".format(
                    self._filename
                )
            )

    def exists(self):
        """
        returns True, if the config file exists
        """
        return os.path.exists(self._filename)

    def save(self):
        """
        save current config to the file
        """
        with open(self._filename, "w") as f:
            self.config.write(f)

    def load(self):
        """
        load existing config file, if existing
        """
        if self.exists():
            # read config file
            self.config.read(self._filename)
