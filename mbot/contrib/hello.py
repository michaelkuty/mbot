
from mbot import Middleware


class Hello(Middleware):

    public = True

    def skip_middleware(self, msg):
        return not ((msg.text and "hello" in msg.text) or
                    msg.text and "hi" != msg.text)

    def process(self, msg):
        """Call `help`\n
        `help airflowtrigger`
        """
        msg.reply("Hello %s" % msg.user)
        return True
