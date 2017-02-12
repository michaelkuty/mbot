from mbot import __version__
from mbot import Middleware


class Config(Middleware):

    def skip_middleware(self, msg):
        return not (msg.text and "conf:" in msg.text and msg.user)

    def process(self, msg):
        """conf:

        conf: disable joker
        conf: enable joker
        """

        if "disable" in msg.text:

            name, new_text = msg._extract_from_text("name", msg.text)

            if msg.backend.disable_middleware(name):

                msg.reply("%s was disabled." % name)

        elif "enable" in msg.text:

            name, new_text = msg._extract_from_text("name", msg.text)

            if msg.backend.enable_middleware(name):

                msg.reply("%s was enabled." % name)

        else:

            msg.reply(
                """
                Slackbot configuration: \n
                *version*: %(version)s \n
                *Plugins*: %(plugins)s \n
                *Botname*: Airflow \n
                *icon_url*: icon_url \n
                """ % {
                    'version': __version__,
                    'plugins': ','.join([
                        f.__class__.__name__ if hasattr(
                            f, "__class__") else f.__name__
                        for f in msg.bot.get_middlewares()])})

    # @property
    # def periodic_jobs(self):
    #     return [{'name': 'update',
    #              'schedule': '1 day',
    #              'cmd': 'bash: date'}]
