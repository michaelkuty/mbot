
import logging
import pprint

from mbot import Middleware
from mbot.decorators import save_command

LOG = logging.getLogger(__name__)


pp = pprint.PrettyPrinter()


class Template(Middleware):

    requirements = ['jinja2']

    parameters = ['template']

    def skip_middleware(self, msg):
        return not (msg.text and msg.user and "template:" in msg.text)

    @save_command
    def process(self, msg):
        """`template: {{ msg.user }}`"""
        msg.reply_snippet("Output for: `%s`.\n " % msg.body['text'],
                          content=msg.text)
