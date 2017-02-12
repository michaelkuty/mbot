
import logging
import sys
import time
from copy import deepcopy
from datetime import datetime
from re import search

import asyncio
import types
from concurrent.futures import ThreadPoolExecutor
from importlib import import_module
from mbot.config import Config
from mbot.exceptions import ShuttingDown
from mbot.middleware import Middleware
from mbot.state import StateMachine
from mbot.storage import S3, Storage
from mbot.utils.packages import install_package
from typing import Any, Callable, List, Optional  # NOQA

LOG = logging.getLogger(__name__)

EXECUTOR_POOL_SIZE = 10

try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


def callback(func: Callable[..., None]) -> Callable[..., None]:
    """Annotation to mark method as safe to call from within the event loop."""
    # pylint: disable=protected-access
    func._callback = True
    return func


def is_callback(func: Callable[..., Any]) -> bool:
    """Check if function is safe to be called in the event loop."""
    return '_callback' in func.__dict__


class Bot:

    """Yet another simple bot

    Has simple in memory global state which is available in middlewares

    :param: middlewares: import strings or callables
    :param: state: optional your state object
    :param: process_types: array of event types default is set to all
    :param: extra: extra dictionary which is available in middlewares
    for example connection strings etc..
    """

    # disable processing for own events
    filter_itself = False

    _backends = []

    possible_storages = {
        's3': 'mbot.storage.S3',
        'local': 'mbot.storage.Storage',
    }

    def __init__(self, backends=None, middlewares=None, state=None,
                 process_types=None, extra={}, state_path=None,
                 storage_engine="local", conf=None,
                 config_path=None, encrypt=True, **kwargs):

        self.process_types = process_types
        self.extra = extra

        self.conf = conf or Config(data_path=state_path,
                                   config_path=config_path,
                                   encrypt=encrypt,
                                   **kwargs)

        self.conf.init()
        self.conf.init_logging()

        if self.conf.storage['encrypt']:
            from cryptography.fernet import Fernet
            self.fernet = Fernet(self.conf.storage["fernet_token"])

        # this is passed to all middlewares
        self.kwargs = kwargs

        # load dynamic parts
        self.load_backends(backends or self.conf.core['backends'])

        StorageCls = self.load_thing(self.possible_storages[storage_engine])

        self.storage = StorageCls(self, encrypt=encrypt, **self.kwargs)

        # state persistence
        try:
            self.state = self.storage.restore_state(self.conf.data_path)
        except:
            self.state = StateMachine(self)

        # initialize pools
        if sys.platform == 'win32':
            self.loop = asyncio.ProactorEventLoop()
        else:
            self.loop = asyncio.get_event_loop()

        self.executor = ThreadPoolExecutor(max_workers=EXECUTOR_POOL_SIZE)
        self.loop.set_default_executor(self.executor)
        self.loop.set_exception_handler(self._async_exception_handler)

    @callback
    def _async_exception_handler(self, loop, context):
        """Handle all exception inside the core loop."""
        kwargs = {}
        exception = context.get('exception')
        if exception:
            # Do not report on shutting down exceptions.
            if isinstance(exception, ShuttingDown):
                return

            kwargs['exc_info'] = (type(exception), exception,
                                  exception.__traceback__)

        LOG.exception("Error doing job: %s", context['message'], **kwargs)

    def load_thing(self, name):
        """Load whatever
        """
        if isinstance(name, str):
            module = import_module(".".join(name.split(".")[:-1]))
            if module:
                return getattr(module, name.split(".")[-1], None)
            raise Exception("Cannot load %s" % name)

    def load_backends(self, backends=[]):
        for m in backends:
            path = self.conf.conf[m]['engine']
            BackendCls = self.load_thing(path)
            if BackendCls:
                self._backends.append(BackendCls(m, self, **self.kwargs))
                continue

    @callback
    def _async_add_job(self, target: Callable[..., None], *args: Any) -> None:
        """Add a job from within the eventloop.
        This method must be run in the event loop.
        target: target to call.
        args: parameters for method to call.
        """
        if asyncio.iscoroutine(target):
            self.loop.create_task(target)
        elif is_callback(target):
            self.loop.call_soon(target, *args)
        elif asyncio.iscoroutinefunction(target):
            self.loop.create_task(target(*args))
        else:
            self.loop.run_in_executor(None, target, *args)

    add_async_job = _async_add_job

    def run_pending_jobs(self):
        """Run all jobs marked for run"""

        now = datetime.now()
        now = now.replace(microsecond=0)

        for key, job in self.state.jobs.all().items():
            if job.when <= now:
                LOG.debug("Run scheduled job: %s" % job)
                job.process(self, now)

    def process_middlewares(self, backend, messages):

        try:
            backend.process_middlewares(messages)
        except Exception as e:
            LOG.exception(e)

    @asyncio.coroutine
    def handle_backend(self, backend) -> None:
        """Run loop action on backend
        """

        if backend.connect():

            while True:

                messages = backend.read()

                self.state.add_new_messages(messages)

                self.add_async_job(self.process_middlewares,
                                   backend, messages)

                self.add_async_job(self.run_pending_jobs)

                time.sleep(1)

        else:
            LOG.info("Connection Failed for %s." % backend)

    @asyncio.coroutine
    def async_stop(self, exit_code=0) -> None:
        """Stop BOT and shuts down all threads.
        This method is a coroutine.
        """

        self.executor.shutdown()
        self.exit_code = exit_code
        self.loop.stop()
        self.state.save()

    def run(self, backends=None) -> None:
        """Run Slackbot
        """

        for backend in backends or self._backends:
            self.loop.create_task(self.handle_backend(backend))

        # Run forever and catch keyboard interrupt
        try:
            # Block until stopped
            LOG.info("Starting BOT core loop")
            self.loop.run_forever()
        except KeyboardInterrupt:
            self.loop.create_task(self.async_stop())
            self.loop.run_forever()
        finally:
            self.loop.close()

    def get_middlewares(self, backends=None):
        middlewares = []
        for b in backends or self._backends:
            middlewares += b.middlewares
        return middlewares

    def get_middleware(self, name=None, backends=None):
        for b in backends or self._backends:
            m = b.get_middleware(name)
            if m:
                return m

    def __getstate__(self):
        state = self.__dict__.copy()
        # Remove the unpicklable entries.
        if 'loop' in state:
            del state['loop']
        if 'executor' in state:
            del state['executor']
        if 'fernet' in state:
            del state['fernet']

        return state

    _instance = None

    def __new__(cls, *args, **kwargs):
        """A singleton implementation of AppLoader. There can be only one.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance
