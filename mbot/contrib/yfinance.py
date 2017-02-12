
import logging
from mbot import Middleware
from mbot.decorators import save_command

LOG = logging.getLogger(__name__)


class YahooFinance(Middleware):

    requirements = ['yahoo-finance', 'BeautifulSoup4', 'plotly']
    public = True
    parameters = ['finance', ('date-from', '2014-01-01'),
                  ('date-to', '2017-01-01')]

    def skip_middleware(self, msg):
        return not (msg.text and msg.user and "finance:" in msg.text)

    @save_command
    def process(self, msg):
        """`plot: hovno`"""

        params = msg.extract_parameters(self.parameters, )

        from bs4 import BeautifulSoup
        from yahoo_finance import Share
        import plotly.plotly as py
        import plotly.graph_objs as go
        from dateutil.parser import parse

        yahoo = Share(params['finance'])

        history = yahoo.get_historical(params['date-from'],
                                       params['date-to'])
        x = [parse(d['Date']) for d in history]
        data = [go.Scatter(x=x, y=[d['Close'] for d in history])]
        f = py.iplot(data)
        soup = BeautifulSoup(f.data, 'html.parser').find_all("iframe")[0]
        msg.reply(soup.get("src"))
