====
MBot
====

.. image:: https://img.shields.io/pypi/v/mbot.svg
        :target: https://pypi.python.org/pypi/mbot

.. image:: https://img.shields.io/travis/michaelkuty/mbot.svg
        :target: https://travis-ci.org/michaelkuty/mbot

.. image:: https://readthedocs.org/projects/mbot/badge/?version=latest
        :target: https://mbot.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/michaelkuty/mbot/shield.svg
     :target: https://pyup.io/repos/github/michaelkuty/mbot/
     :alt: Updates


Yet another Bot implemented in pure Python. Is designed to support multiple backends with global state machine which can store shortcuts for your commands and more. Support user permissions for actions.

* Free software: MIT license
* Documentation: https://mbot.readthedocs.io.

|Animation|

Message Backends
----------------

* Slack
* MQTT (TODO)
* RabbitMQ (TODO)

Storage Backends
----------------

* Local file
* S3 file
* Support encryption in default
* DB (TODO)

Middlewares
-----------

* Slack
* SQL
* AirflowTrigger
* Bash
* Saltstack (pepper client)
* Joker (say some joke)
* History (list of your commands, save shortcuts)
* Help

Features
--------

* Simple scheduler
* User roles and permissions
* Filebased config/state
* Encrypted storage
* Connections management
* S3 storage
* Dialogs
* Auto installing of dependencies
* Dynamic loading

Installation
------------

.. code-block:: bash

    pip install mbot

Usage
-----

.. code-block:: bash

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

TODO
----

* Variables, management
* Support Celery as executor
* SSH
* Use appdirs when data-path is not provied

.. |Animation| image:: https://github.com/michaelkuty/mbot/raw/master/docs/images/animation.gif