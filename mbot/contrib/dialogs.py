
from mbot import Middleware


class Dialogs(Middleware):

    public = True

    parameters = ["dialog"]

    def skip_middleware(self, msg):
        return not (msg.text and msg.user and "dialog:" in msg.text)

    def process(self, msg):
        """
        `dialog:` list of connection\n
        `dialog: name` show dialog by name\n
        """

        params = msg.extract_parameters(["dialog"])

        if "help" in msg.text:
            dialog = msg.bot.state.dialogs.get(params['dialog'], msg.user)
            if dialog:
                msg.reply("Helptext for current step: %s" % dialog.get_help())
            else:
                msg.reply("Dialog with name: %s not found." % params)
            return True
        else:
            msg.reply("Current dialogs %s" % {
                d.name: d.get_info()
                for key, d in msg.bot.state.dialogs.all(msg.user).items()
                if hasattr(d, "get_info")})
