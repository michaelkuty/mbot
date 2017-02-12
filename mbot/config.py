# -*- coding: utf-8 -*-

import logging
import os

import anyconfig
import appdirs
from mbot.utils.packages import install_package

LOG = logging.getLogger(__name__)

__name__ = "mbot"
__author__ = "Michael Kuty"

DATA_PATH = appdirs.user_data_dir(__name__, __author__)
CONFIG_PATH = appdirs.user_config_dir(__name__, __author__)

CONFIG_FORMAT = "yaml"

DEFAULT_CONFIG = """
core:
  data_path: {data_path}
  config_path: {config_path}
  backends:
    - slack

slack:
  token: {slack_token}
  engine: mbot.backends.slack.Slack
  middlewares:
    - mbot.contrib.system.Config
    - mbot.contrib.history.history
    - mbot.contrib.debug.Debug
    - mbot.contrib.bash.Bash
    - mbot.contrib.console.MBotConsole
    - mbot.contrib.python.Python
    - mbot.contrib.joker.Joker
    - mbot.contrib.hackernews.HackerNews
    - mbot.contrib.scheduler.Scheduler
    - mbot.contrib.salt.Salt
    - mbot.contrib.connections.Connections
    - mbot.contrib.dialogs.Dialogs
    - mbot.contrib.airflow.AirflowTrigger
    - mbot.contrib.sql.SQL
    - mbot.contrib.help.Help

storage:
  engine: local
  encrypt: {encrypt}
  fernet_token: {fernet_token}

logging:
  verbosity: INFO
"""


class Config:

    @property
    def backends(self):
        _b = []
        backends = self.conf['core'].get("backends", [])
        for b in backends:
            _b.append(self.conf[b]["engine"])
        return _b

    @property
    def middlewares(self):
        _b = []
        backends = self.conf['core'].get("backends", [])
        for b in backends:
            _b.append(self.conf[b].get("middlewares", []))
        return _b

    @property
    def storage(self):
        return self.conf['storage']

    @property
    def core(self):
        return self.conf['core']

    @property
    def logging(self):
        return self.conf['logging']

    def init_logging(self):
        """Init logging"""

        if not self.is_ready():
            return

        if 'sentry_dsn' in self.logging:
            install_package("raven")
            from raven import Client
            self.sentry = Client(self.logging['sentry_dsn'])

        logging.basicConfig(level=getattr(logging,
                                          self.logging['verbosity'],
                                          logging.DEBUG))

    def init(self):
        """Create directories and loads config"""

        directory = '/'.join(self.data_path.split("/")[:-1])

        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        cf_directory = '/'.join(self.config_path.split("/")[:-1])

        if cf_directory and not os.path.exists(cf_directory):
            os.makedirs(cf_directory)

        if not os.path.exists(self.config_path):

            if self.encrypt and not hasattr(self, "fernet_token"):
                try:
                    from cryptography.fernet import Fernet
                except ImportError:
                    install_package("cryptography")
                self.fernet_token = Fernet.generate_key().decode("utf-8")

            ctx = self.__dict__.copy()
            ctx.update({
                'data_path': self.data_path,
                'config_path': self.config_path
            })

            try:
                with open(self.config_path, "w+") as f:
                    cf = DEFAULT_CONFIG.format(**ctx)
                    LOG.debug(cf)
                    f.write(cf)
            except Exception as e:
                LOG.exception(e)
                raise Exception("Cannot initialize new config file")

        self.load()

    def load(self):
        try:
            self.conf = anyconfig.load(self.config_path, CONFIG_FORMAT)
        except Exception as e:
            LOG.error("Failed load config file %s" % e)

    @property
    def data_path(self):
        if not self._data_path:
            return os.path.join(DATA_PATH, "state.db")
        return self._data_path

    @property
    def config_path(self):
        if not self._config_path:
            return os.path.join(CONFIG_PATH, "mbot.conf")
        return self._config_path

    def is_ready(self, key=None):
        """Generic checker
        :param:key: string slack.token
        """
        if key:
            group, k = key.split(".")
            return k in self.conf.get(group, {})
        return 'backends' in self.conf.get('core', {})

    def __init__(self, data_path=None, config_path=None, **kwargs):
        self.conf = {}
        self._data_path = data_path
        self._config_path = config_path

        for key, value in kwargs.items():
            setattr(self, key, value)
