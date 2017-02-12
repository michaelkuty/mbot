
import logging
import delegator
from mbot import Middleware
from mbot.decorators import save_command

LOG = logging.getLogger(__name__)


class Salt(Middleware):

    requirements = ['salt-pepper']

    groups = ['devops', 'admin', 'sysadmin']
    permissions = ['salt-call']

    def skip_middleware(self, msg):
        return not (msg.text and msg.user and "salt:" in msg.text)

    @save_command
    def process(self, msg):
        """`salt: test.ping nodes: *`"""
        command = msg.text.replace("salt:", "")

        nodes, command = msg._extract_from_text("nodes", command,
                                                r':\s?(\w*.+|"[^"]+")')

        cmd = 'pepper'

        if "-C" in nodes:
            cmd = 'pepper %s %s' % (nodes, command)
        else:
            cmd = 'pepper "%s" %s' % (nodes, command)

        r = delegator.run(cmd)

        msg.reply_snippet("Output for: `%s`.\n " % cmd,
                          content=r.out or r.err)
