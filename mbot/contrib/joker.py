from pyjokes.pyjokes import get_joke

from mbot import Middleware


class Joker(Middleware):

    public = True

    requirements = ["pyjokes"]

    def skip_middleware(self, msg):
        return not (msg.text and "joke" in msg.text and 'channel' in msg.body)

    def process(self, msg):
        """`joke`"""
        msg.reply(get_joke(category="all"))
