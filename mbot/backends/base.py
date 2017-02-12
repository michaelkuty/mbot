
import logging
import types

from copy import deepcopy
from mbot.event import Event
from mbot.utils.packages import install_package

LOG = logging.getLogger(__name__)


class Dispatcher:

    """Interface for bot backends

    Set your client under client property
    which is not serialized into state

    """

    @property
    def code(self):
        """Returns name"""
        return self.__class__.__name__.lower()

    def __init__(self, name, bot, *args, **kwargs):
        self.bot = bot
        self.name = name
        self._middlewares = []
        self.conf = self.bot.conf.conf[name]

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.load_middlewares(self.conf['middlewares'])

    def connect(self):
        """Returns True if connection is successfull"""

        raise NotImplementedError

    def read(self):
        """Return array of messages"""
        raise NotImplementedError

    def send(self, *args, **kwargs):
        """Send message"""
        raise NotImplementedError

    def reply(self, message, *args, **kwargs):
        """Reply to a message"""
        raise NotImplementedError

    def load_middlewares(self, names=[]):
        """Load new middlewares
        """

        for m in (names or self.middlewares):

            if not callable(m) and isinstance(m, str):

                func = self.bot.load_thing(m)

                if (func and callable(func) and
                        isinstance(func, types.FunctionType)):

                    self._middlewares.append(func)
                    continue

                elif func:
                    middleware = func()

                    for package in getattr(middleware,
                                           "requirements", []):
                        install_package(package)

                    self._middlewares.append(middleware)
                    continue

            elif callable(m):
                self._middlewares.append(m)

        self._all_middlewares = deepcopy(self.middlewares)

    @property
    def middlewares(self):
        return self._middlewares

    def get_middleware(self, name):

        for m in self.middlewares:
            if hasattr(m, "code"):
                if m.code == name:
                    return m
            elif m.__name__ == name:
                return m

    def disable_middleware(self, name):

        for i, m in enumerate(self.middlewares):
            if m.__name__ == name:
                self._middlewares.pop(i)
                return True

    def enable_middleware(self, name):

        self.load_middlewares([name])

        return True

    def process_events(self, events):
        """Returns new events
        """

        _events = []

        for event in events:

            # skip event types
            msg_type = event.get("type", None)

            if msg_type and self.bot.process_types:
                if msg_type not in self.process_types:
                    continue

            _events.append(Event(self.bot, self, event))

        return _events

    def process_middleware(self, middleware, msg):
        # process functions

        if not isinstance(middleware, types.FunctionType):

            if middleware.skip_message(msg):
                return

            msg = middleware.pre_process(msg)

            skip_others = middleware.process(msg)
            middleware.post_process(msg)
            return skip_others
        else:
            return middleware(msg)

    def process_middlewares(self, messages, silently=False):
        """Call middlewares for all messages
        """

        for msg in messages:

            for middleware in self.middlewares:

                try:
                    if middleware.skip_middleware(msg):
                        continue
                except:
                    pass

                try:
                    if not middleware.check_permissions(msg):
                        msg.reply("Permission denied for %s" % middleware)
                        continue
                except:
                    pass

                try:
                    skip_others = self.process_middleware(
                        middleware, msg)
                except Exception as e:
                    if not silently:
                        raise e
                    LOG.exception(e)

                if skip_others:
                    break

    def get_users(self):
        """Returns dictionary of users"""
        return {}

    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        if 'client' in state:
            del state['client']
        if '_all_middlewares' in state:
            del state['_all_middlewares']
        if '_middlewares' in state:
            del state['_middlewares']
        return state
