
import logging
import pprint

from mbot import Middleware
from mbot.decorators import save_command

LOG = logging.getLogger(__name__)


pp = pprint.PrettyPrinter()


class SQL(Middleware):

    code = 'sql'

    requirements = ['records']

    parameters = ['sql', 'db', ('format', 'xls')]

    def skip_middleware(self, msg):
        return not (msg.text and msg.user and "sql:" in msg.text)

    @save_command
    def process(self, msg):
        """`sql: select count(*) from stories; db: mydb format: xls`"""

        params = msg.extract_parameters(self.parameters)

        params.update(msg.extract_parameters(
            ['sql'], r":\s?(\S*['-]* .*;|\w*.+|'[^']+')"))

        conn = msg.bot.state.connections.get(params['db'])

        if not conn:
            msg.reply("Connection not found *%s*" % (params['db']))

        import records

        db = records.Database(conn.uri)

        result = db.query(params['sql'])

        msg.reply_snippet("Output for: `%s`.\n " % params['sql'],
                          format=params['format'],
                          file=result.export(params['format']),
                          ext=params['format'])
