
import logging
from mbot import Middleware
from mbot.decorators import save_command
import requests
import io
from slugify import slugify


LOG = logging.getLogger(__name__)


class ScreenshotLayer(Middleware):

    requirements = ['requests']
    public = True
    parameters = [('url', None)]

    def skip_middleware(self, msg):
        return not (msg.text and msg.user and "screenshot:" in msg.text)

    @save_command
    def process(self, msg):
        """`plot: hovno`"""

        params = msg.extract_parameters(self.parameters, )

        url = "http://api.screenshotlayer.com/api/capture"

        response = requests.get(url, params={'access_key': '445a097be18bef09018bceefde312807',
                                             'url': params['url'][1:-1]}, stream=True)

        response.raise_for_status()
        response.raw.decode_content = True

        name = slugify(params['url'])
        kwargs = {
            'filetype': "png",
            'channels': msg.body['channel'],
            'filename': '.'.join([name, "png"]),
            'initial_comment': name,
            'title': name,
            'file': response.raw.read()
        }

        msg.reply("Your screenshot ", attachments=[kwargs])
