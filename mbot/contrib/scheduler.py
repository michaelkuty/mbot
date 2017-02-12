
import logging
import pprint
from datetime import datetime

import humanize
import parsedatetime
from mbot import Middleware
from mbot.decorators import save_command

LOG = logging.getLogger(__name__)


pp = pprint.PrettyPrinter()


class Scheduler(Middleware):

    public = True

    parameters = [('schedule', '1 minute'), 'cmd']

    def skip_middleware(self, msg):
        return not (msg.text and msg.user and "schedule:" in msg.text)

    @save_command
    def process(self, msg):
        """
        `schedule: 10s cmd: test`
        `schedule: every friday cmd: test`
        `schedule: every friday at 10:30 cmd: test`
        """

        params = msg.extract_parameters(
            ['schedule'], r"\s?(.*cmd:?|\S*['-]*|\w*.+|'[^']+')")

        params.update(msg.extract_parameters(['cmd']))

        if params['cmd'] is not None:
            cal = parsedatetime.Calendar()

            try:
                when, status = cal.parse(params['schedule'])
                when = datetime(*when[:6])
            except Exception as e:
                msg.reply("Cannot parse %s with %s" % (when, e))
                return True

            msg.bot.state.jobs.update(params['cmd'], {
                'every': "every" in params['schedule'],
                'when': when,
                'raw': params,
                'delta': when - datetime.now().replace(microsecond=0),
                'cmd': params['cmd'],
                'user': msg.user
            })
            msg.reply("Your job: %s is scheduled in %s. %s" % (
                params['cmd'], humanize.naturaltime(when), when))
        else:
            msg.reply("Your jobs: %s" % '\n'.join([
                j.__repr__() for j in msg.bot.state.jobs.all()]))
