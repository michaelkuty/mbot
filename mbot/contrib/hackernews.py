
from mbot import Middleware
from mbot.decorators import save_command


class HackerNews(Middleware):

    public = True

    parameters = [("hn", "last"), ("limit", "15")]
    requirements = ["haxor"]

    def skip_middleware(self, msg):
        return not (msg.text and msg.user and "hn:" in msg.text)

    @save_command
    def process(self, msg):
        """
        `hn:` top\n
        `hn: last
        """

        params = msg.extract_parameters(self.parameters)

        from hackernews import HackerNews
        hn = HackerNews()

        [msg.reply("{title} - {score} - {url}".format(**hn.get_item(s).__dict__))
         for s in (hn.new_stories(int(params['limit']))
                   if params['hn'] == "last" else
                   hn.top_stories(int(params['limit'])))]

        return True
