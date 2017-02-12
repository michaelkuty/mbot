
from mbot import Middleware, Dialog


class Connections(Middleware):

    requirements = ['delegator']
    parameters = ["conn", "name", "schema", "username",
                  "password", "host", "port",
                  "engine", "uri"]

    def skip_middleware(self, msg):
        return not (msg.text and msg.user and "conn:" in msg.text)

    def process(self, msg):
        """
        `conn:` list of connections\n
        `conn: set name: test db: name password: password host: localhost port: 5432 engine: postgresql`
        """

        def step1(dialog, msg, params):
            """Fill required parameters and confirm parsing"""
            msg.reply("Check your params: %s and say Yes! or No! to fill again" % ','.join([
                str(h) for h in params.items()]))
            return params

        def step2(dialog, msg, params):
            """Fill required parameters and confirm parsing"""

            data = dialog.get_step_data(0)

            if "yes" in msg.text:
                del data['conn']
                msg.reply("I store your connection "
                          "with params: %s" % data)
                data['uri'] = data['uri'][1:-1]
                msg.bot.state.connections.set(
                    data['name'], data)
                msg.reply("New connection "
                          "with params: %s" % data)

            return True

        if "list" in msg.text:
            msg.reply("Connections %s" % msg.bot.state.connections.get_info())
            return True
        else:
            dialog = Dialog(msg, "connection",
                            actions=[(step1, self.parameters),
                                     (step2, ['conn'])])

            return dialog.process()
