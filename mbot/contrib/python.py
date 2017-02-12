
import pprint
from mbot import Middleware
from mbot.decorators import save_command

pp = pprint.PrettyPrinter()


class Python(Middleware):

    public = True

    def skip_middleware(self, msg):
        return not (msg.text and msg.user and "python:" in msg.text)

    @save_command
    def process(self, msg):
        """`python: abs(-3)`"""

        params = msg.extract_parameters(["python"],
                                        r":\s?(\S*['-]* .*|\w*.+|'[^']+')")

        command = params['python']

        try:
            result = eval(command, globals(), {
                'bot': msg.bot,
                'state': msg.bot.state,
            })
        except Exception as e:
            result = e

        msg.reply_snippet("Output for: `%s`.\n " % command,
                          content=pp.pformat(result))
