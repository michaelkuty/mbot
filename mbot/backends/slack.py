
import logging

from mbot.event import Event
from mbot.state import User
from mbot.utils.packages import install_package

from .base import Dispatcher

LOG = logging.getLogger(__name__)


class Slack(Dispatcher):

    """Yet another simple bot

    Uses slack RTM and calls middlewares for all messages

    :param: slack_token: slack token
    """

    @property
    def sc(self):
        """Returns slack client"""
        if not hasattr(self, "client"):
            try:
                from slackclient import SlackClient
            except ImportError:
                install_package("slackclient")

            self.client = SlackClient(self.conf['token'])

        return self.client

    def connect(self):
        """Returns True if connection is successfull"""
        try:
            return self.sc.rtm_connect()
        except Exception as e:
            LOG.exception(e)

    def upload(self, data, initial_comment=None, channel=None):
        if isinstance(data, list):
            results = []
            for datum in data:
                results.append(self.sc.api_call(
                    "files.upload",
                    channel=channel,
                    **datum))
            return results

        response = self.sc.api_call(
            "files.upload",
            channel=channel,
            attachments=data)
        LOG.debug(response)
        return response

    def read(self):

        try:
            events = self.sc.rtm_read()
        except:
            self.connect()
            try:
                events = self.sc.rtm_read()
            except Exception as e:
                LOG.exception(e)

        return self.process_events(events)

    def send(self, *args, **kwargs):
        return self.sc.rtm_send_message(*args, **kwargs)

    def reply(self, message, text, attachments=None, *args, **kwargs):
        """Reply to a message"""
        if 'channel' not in message.body:
            LOG.error("Cannot reply on message %s" % message)
            return

        if attachments:
            return self.upload(attachments, text, message.body['channel'])

        return self.send(message.body['channel'], text, *args, **kwargs)

    @property
    def author_id(self):
        if not hasattr(self, "_author_id"):
            self._author_id = self.sc.api_call("auth.test")['user_id']
        return self._author_id

    def process_events(self, events):
        """Returns new events
        """

        _events = []

        for event in events:

            # skip own events
            if 'user' in event and event['user'] == self.author_id:
                continue

            # skip event types
            msg_type = event.get("type", None)

            if msg_type and self.bot.process_types:
                if msg_type not in self.process_types:
                    continue

            _events.append(Event(self.bot, self, event))

        return _events

    def get_users(self):
        """Returns dictionary of users"""
        try:
            members = self.sc.api_call("users.list")['members']
        except:
            members = []
        return {u['id']: User(**{
            'name': u['name'],
            'real_name': u['real_name'],
            'is_bot': u['is_bot'],
            'id': u['id'],
        }) for u in members}
