
from mbot import Middleware
from mbot.decorators import save_command


class Help(Middleware):

    public = True

    def skip_middleware(self, msg):
        return not (msg.text and "help" in msg.text)

    @save_command
    def process(self, msg):
        """Call `help`\n
        `help airflowtrigger`
        """

        mid = msg.text.replace("help", "").strip()

        if mid:
            m = msg.bot.get_middleware(mid)
            if m:
                if hasattr(m, "process"):
                    doc = m.process.__doc__
                    if doc:
                        msg.reply(m.process.__doc__)
                else:
                    doc = m.__doc__
                    if doc:
                        msg.reply(m.__doc__)
            else:
                msg.reply("Function %s not found." % mid)
        else:
            msg.reply(self.process.__doc__)

        return True
