
import logging
import os

from mbot import Middleware

LOG = logging.getLogger(__name__)


class Debug(Middleware):

    public = True

    def skip_middleware(self, msg):
        return not os.environ.get("DEBUG", False)

    def process(self, msg):
        LOG.debug(msg)
