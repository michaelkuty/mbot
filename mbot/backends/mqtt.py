
import logging

from mbot.event import Event
from mbot.utils.packages import install_package

from .base import Dispatcher

LOG = logging.getLogger(__name__)


def on_connect(client, userdata, flags, rc):
    LOG.debug("Connected with result code " + str(rc))

    for sub in client.mbot.conf.conf[client.backend.name]['subscribe']:
        client.subscribe(sub)


def on_message(client, userdata, msg):
    events = client.backend.process_events([msg])
    client.mbot.add_async_job(client.backend.process_middlewares,
                              events)


class MQTT(Dispatcher):

    """
    config::
        mqtt:
          engine: mbot.backends.mqtt.MQTT
          host: localhost
          subscribe:
            - "$SYS/#"
          middlewares:
            - mbot.contrib.debug.Debug
    """

    own_loop = True

    def start_loop(self):
        self.connect()
        self.mqtt.loop_start()

    def stop_loop(self):
        self.mqtt.loop_stop(force=True)

    @property
    def mqtt(self):
        """Returns slack client"""
        if not hasattr(self, "client"):
            try:
                import paho.mqtt.client as mqtt
            except ImportError:
                install_package("paho-mqtt")

            self.client = mqtt.Client()
            self.client.on_connect = on_connect
            self.client.on_message = on_message
            self.client.mbot = self.bot
            self.client.backend = self

        return self.client

    def connect(self):
        """Returns True if connection is successfull"""
        try:
            return self.mqtt.connect(
                self.conf['host'],
                port=self.conf.get('port', 1883),
                keepalive=self.conf.get('keepalive', 60))
        except Exception as e:
            LOG.exception(e)

    def read(self):
        return []

    def send(self, *args, **kwargs):
        raise NotImplementedError

    def reply(self, message, text, attachments=None, *args, **kwargs):
        """Reply to a message"""
        raise NotImplementedError

    def process_events(self, events):
        return [Event(self.bot, self, event) for event in events]
