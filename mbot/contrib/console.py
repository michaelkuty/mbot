
import pprint
from mbot import Middleware
from mbot.decorators import save_command

pp = pprint.PrettyPrinter()


class MBotConsole(Middleware):

    public = True

    def skip_middleware(self, msg):
        return not (msg.text and msg.user and "mbot:" in msg.text)

    @save_command
    def process(self, msg):
        """`python: abs(-3)`"""

        params = msg.extract_parameters(["mbot"],
                                        r":\s?(\S*['-]* .*|\w*.+|'[^']+')")

        command = params['mbot']

        ctx = {'bot': msg.bot,
               'state': msg.bot.state}

        for key, val in msg.bot.state._states.items():
            ctx[key] = getattr(msg.bot.state, key)

        try:
            result = eval(command, globals(), ctx)
        except Exception as e:
            result = e

        msg.reply_snippet("Output for: `%s`.\n " % command,
                          content=pp.pformat(result))
