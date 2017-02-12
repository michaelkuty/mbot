
import logging
from mbot import Middleware
from mbot.decorators import save_command

LOG = logging.getLogger(__name__)


class Bash(Middleware):

    public = True
    requirements = ['delegator.py']
    parameters = [('bash', 'date')]

    def skip_middleware(self, msg):
        return not (msg.text and msg.user and "bash:" in msg.text)

    @save_command
    def process(self, msg):
        """bash: fortune | cowsay"""

        params = msg.extract_parameters(self.parameters,
                                        r":\s?(\S*['-]* .*|\w*.+|'[^']+')")

        command = params['bash']

        import delegator

        LOG.debug(command)

        r = delegator.run(command)

        LOG.debug(r.out)

        if r.err:
            LOG.debug(r.err)

        msg.reply_snippet("Output for: `%s` " % command,
                          r.out or r.err)
