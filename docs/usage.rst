=====
Usage
=====

To use MBot in a project::

    $ mbot run
    Slack token: xoxb-46465446310727-654564564564654565456
    Starting your BOT...
    INFO:requests.packages.urllib3.connectionpool:Starting new HTTPS connection (1): slack.com

Config

.. code-block:: bash

    $ mbot config
    {'core': {'backends': ['slack'],
              'config_path': '/Users/user/Library/Application '
                             'Support/mbot/mbot.conf',
              'data_path': '/Users/user/Library/Application '
                           'Support/mbot/state.db'},
     'logging': {'verbosity': 'INFO'},
     'slack': {'engine': 'mbot.backends.slack.Slack',
               'middlewares': ['mbot.contrib.system.Config',
                               'mbot.contrib.history.history',
                               'mbot.contrib.debug.Debug',
                               'mbot.contrib.bash.Bash',
                               'mbot.contrib.console.MBotConsole',
                               'mbot.contrib.python.Python',
                               'mbot.contrib.joker.Joker',
                               'mbot.contrib.hackernews.HackerNews',
                               'mbot.contrib.scheduler.Scheduler',
                               'mbot.contrib.salt.Salt',
                               'mbot.contrib.connections.Connections',
                               'mbot.contrib.dialogs.Dialogs',
                               'mbot.contrib.airflow.AirflowTrigger',
                               'mbot.contrib.sql.SQL',
                               'mbot.contrib.help.Help'],
               'token': 'xoxb-46465446310727-654564564564654565456'},
     'storage': {'encrypt': True,
                 'engine': 'local',
                 'fernet_token': 'oMdNGsFou566j4e3SL6cij3HR70D-xIqh58z30B2BAs='}}

Add user to admin group

.. code-block:: bash

    mbot: users.all()

.. code-block:: bash

    mbot: users.update("your_user_id", ["admin"], "groups")

Storing commands
----------------

.. code-block:: bash

    save my last command name: test
    save my command index: 0 name: test

List of commands

.. code-block:: bash

    list

Help
----

.. code-block:: bash

    help history
    help salt

Scheduled Jobs
--------------

.. code-block:: bash

    mbot: jobs.all()

delete

.. code-block:: bash

    mbot: jobs.delete("name")