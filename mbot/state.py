
import logging
import os
import re
from datetime import datetime
from urllib.parse import urlparse

import humanize
import parsedatetime
from mbot.event import Event
from mbot.utils import merge

LOG = logging.getLogger(__name__)


class Manager(object):

    """Simple manager util for storing data related to the group
    """

    item_class = None

    def __init__(self, states, user_states,
                 name=None, scope=None, *args, **kwargs):

        self.name = name or self.name
        self.scope = scope or self.scope
        self.states = states
        self.user_states = user_states

    def update(self, key, item, attr=None):
        data = self.get(key)
        LOG.debug("Update key: %s, attr: %s item %s data %s",
                  key, attr, item, data)
        if data:

            if self.item_class and isinstance(data, self.item_class):
                if attr and hasattr(data, attr):
                    setattr(data, attr, item)
            else:
                try:
                    _data = data.get(attr, data)
                except:
                    _data = getattr(data, attr, data)

                try:
                    _data = merge(_data, item)
                except:
                    pass

                if hasattr(data, attr):
                    setattr(data, attr, _data)
                elif isinstance(data, dict) and attr in data:
                    data[attr] = _data
                else:
                    setattr(data, attr, _data)

        return self.set(key, data or item)

    def get_many(self, wildcard, user=None):
        if user:
            states = self.user_states[user]
        else:
            states = self.states
        return {key: states[key] for key in states.keys()
                if re.match(wildcard, key)}

    def get_info(self, user=None):
        return {d.name: d
                for key, d in self.all(user).items()
                if hasattr(d, "name")}

    def all(self, user=None):

        key = '{0}.{1}*'.format(self.name, self.scope)

        if user:
            self.init_user_space(user)
        return self.get_many(key, user)

    def init_user_space(self, user):
        if user not in self.user_states:
            self.user_states[user] = {}

    def set(self, key, data, user=None, raw=False):

        if self.item_class and not raw:
            if isinstance(data, dict):
                data = self.item_class(**data)
            elif isinstance(data, list):
                data = [self.item_class(**d)
                        for d in data]

        if user:
            self.init_user_space(user)
            self.user_states[user][self.get_key(key)] = data
        else:
            self.states[self.get_key(key)] = data

    def get(self, key, user=None):
        if user:
            self.init_user_space(user)
            return self.user_states[user].get(self.get_key(key), None)
        return self.states.get(self.get_key(key), None)

    def delete(self, key, user=None):
        if user:
            self.init_user_space(user)
            states = self.user_states[user]
        else:
            states = self.states

        if self.get_key(key) in states:
            del states[self.get_key(key)]

    def get_key(self, key):
        return '{0}.{1}.{2}'.format(self.name, self.scope, key)

    _instance = None

    def __new__(cls, *args, **kwargs):
        """A singleton implementation of Manager. There can be only one.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance


class Connection:

    """
    Placeholder to store information about different database instances
    connection information. The idea here is that scripts use references to
    database instances (conn_id) instead of hard coding hostname, logins and
    passwords when using operators or hooks.
    """

    _types = [
        ('fs', 'File (path)'),
        ('ftp', 'FTP',),
        ('google_cloud_platform', 'Google Cloud Platform'),
        ('hdfs', 'HDFS',),
        ('http', 'HTTP',),
        ('hive_cli', 'Hive Client Wrapper',),
        ('hive_metastore', 'Hive Metastore Thrift',),
        ('hiveserver2', 'Hive Server 2 Thrift',),
        ('jdbc', 'Jdbc Connection',),
        ('mysql', 'MySQL',),
        ('postgresql', 'Postgres',),
        ('oracle', 'Oracle',),
        ('vertica', 'Vertica',),
        ('presto', 'Presto',),
        ('s3', 'S3',),
        ('samba', 'Samba',),
        ('sqlite', 'Sqlite',),
        ('ssh', 'SSH',),
        ('cloudant', 'IBM Cloudant',),
        ('mssql', 'Microsoft SQL Server'),
        ('mesos_framework-id', 'Mesos Framework ID'),
        ('jira', 'JIRA',),
    ]

    def __init__(
            self, name=None, engine=None,
            host=None, username=None, password=None,
            schema=None, port=None, extra=None,
            uri=None):
        self.name = name
        if uri:
            self.parse_from_uri(uri)
        else:
            self.engine = engine
            self.host = host
            self.username = username
            self.password = password
            self.schema = schema
            self.port = port
            self.extra = extra

    def parse_from_uri(self, uri):
        temp_uri = urlparse(uri)
        self.uri = uri
        hostname = temp_uri.hostname or ''
        if '%2f' in hostname:
            hostname = hostname.replace('%2f', '/').replace('%2F', '/')
        conn_type = temp_uri.scheme
        self.conn_type = conn_type
        self.host = hostname
        self.schema = temp_uri.path[1:]
        self.login = temp_uri.username
        self.password = temp_uri.password
        self.port = temp_uri.port


class ConnectionManager(Manager):

    scope = 'connections'
    item_class = Connection


class DialogManager(Manager):

    scope = 'dialogs'


class User:

    def __repr__(self):
        return "%s" % self.__dict__

    def __init__(self, **kwargs):
        self.groups = []
        self.permissions = []
        for key, value in kwargs.items():
            setattr(self, key, value)

    def has_permissions(self, middleware):

        if middleware.public:
            return True

        for group in middleware.groups:
            if group in self.groups:
                return True

        for perm in middleware.permissions:
            if perm in self.permissions:
                return True

        return False


class UserManager(Manager):

    scope = 'users'

    def load(self, bot):
        for m in bot._backends:
            users = getattr(m, "get_users")()
            LOG.debug("Successfully loaded %s users." % len(users))
            for id, user in users.items():
                self.update(str(id).lower(), user)

    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load(bot)


class GroupManager(Manager):

    scope = 'groups'

    def load(self, bot):
        for backend in bot._backends:
            for m in backend.middlewares:
                if hasattr(m, "code"):
                    self.set(backend.code + "." + m.code, {
                        'groups': getattr(m, "groups", []),
                        'permissions': getattr(m, "permissions", []),
                    })

    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load(bot)


class Job:

    def process(self, bot, now=None):

        if not self.has_next():
            bot.state.jobs.delete(self.cmd)
        else:
            self.update_next(bot, now)

        self.last_start = now or datetime.now()

        bot.state.run_command(self.cmd, user=self.user)

        self.last_finished = now or datetime.now()
        self.history.append(self.last_start)

    def update_next(self, bot, now):
        bot.state.jobs.update(self.cmd,
                              self.get_next(now), "when")

    def has_next(self):
        if not self.every:
            return False
        return self.get_next() >= datetime.now()

    def get_next(self, now=None):
        cal = parsedatetime.Calendar()
        when, status = cal.parse(self.raw['schedule'])
        next_run = datetime(*when[:6])

        if now and hasattr(self, "delta"):
            return (now + self.delta).replace(microsecond=0)

        return next_run

    def human_next(self):
        return humanize.naturaldelta(self.get_next())

    def __repr__(self):
        return "<%s-%s>" % (
            humanize.naturaltime(self.get_next()),
            self.cmd)

    def __init__(self, **kwargs):
        self.history = []
        self.every = False
        self.last_start = None
        for key, value in kwargs.items():
            setattr(self, key, value)


class JobManager(Manager):

    scope = 'jobs'
    item_class = Job

    def load(self, bot):
        for backend in bot._backends:
            for m in backend.middlewares:
                if hasattr(m, "code"):
                    for job in m.periodic_jobs:
                        job['raw'] = job
                        self.set(".".join([backend.code,
                                           m.code, job['name']]), job)

    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load(bot)


class StateMachine:

    """Simple state machine object (only in-memory now)

    """

    _states = {
        'connections': ConnectionManager,
        'dialogs': DialogManager,
        'groups': GroupManager,
        'users': UserManager,
        'jobs': JobManager,
    }

    def __init__(self, bot, engine="memory", state_path=None):
        self.engine = engine
        self.bot = bot
        self.state_path = state_path
        # history of command
        self.command_history = {}

        self.states = {}
        self.user_states = {}

        for key, manager in self._states.items():
            setattr(self, key, manager(states=self.states,
                                       user_states=self.user_states,
                                       engine=engine,
                                       name=key,
                                       scope=key,
                                       bot=bot))

        # stored user based command history
        self.commands = {}

        # raw event history
        self.events = []

    def add_new_messages(self, messages):
        self.events += messages

    def save(self):
        return self.bot.storage.save_state(self)

    def get_last_command(self, user):
        if user not in self.command_history:
            self.command_history[user] = []
            return
        if not self.command_history[user]:
            return
        return self.command_history[user][-1]

    def save_command_from_history(self, user, index, name):
        """Story command under new shortcut
        """

        cmd = self.command_history[user][index]

        self.commands[user][name] = cmd

    def save_last_command(self, user, name):
        """Story command under new shortcut
        """

        if user not in self.commands:

            self.commands[user] = {}

        self.commands[user][name] = self.get_last_command(user)

    def get_command(self, user, name):
        if user in self.commands:
            if name in self.commands[user]:
                return self.commands[user][name]
            return False
        return None

    def save_command(self, user, func, args=(), kwargs={}):
        """Store callables with arguments
        """

        if user not in self.command_history:
            self.command_history[user] = []

        self.command_history[user].append((func, args, kwargs))

        self.save()

    def run_command(self, name, user=None, msg=None):
        """Run command stored in user space"""

        func, args, kwargs = self.get_command(user or msg.user, name)

        if msg:
            msg.reply("Loading command *%s*." % name)
            if isinstance(args[1], Event):
                args[1].backend = msg.backend

        LOG.info("%s %s %s " % (func, args, kwargs))

        if isinstance(args[1], Event):
            args[1].bot = self.bot

        func(*args, **kwargs)

    def __repr__(self):
        return "<command_history:%s>" % self.command_history
