
import logging

from mbot import Middleware

LOG = logging.getLogger(__name__)


class Debug(Middleware):

    public = True

    def skip_middleware(self, msg):
        return not msg.bot.conf.debug

    def process(self, msg):
        LOG.debug(msg)
