import logging

from importlib import import_module
from mbot import Middleware

LOG = logging.getLogger(__name__)


class AirflowTrigger(Middleware):

    groups = ['admin', 'airflow']

    parameters = ['airflow', 'dag']

    def skip_middleware(self, msg):
        return not (msg.text and "airflow" in msg.text and
                    "trigger_dag" in msg.text and 'channel' in msg.body)

    def process(self, msg):
        """`airflow trigger_dag name: bonavita_master`
        """

        params = msg.extract_parameters("dag")

        dag_name = params['dag']

        msg.reply(
            "OK, my friend ! I will trigger %s" % dag_name)

        from airflow import api, conf

        api.load_auth()
        api_module = import_module(conf.get('cli', 'api_client'))
        api_client = api_module.Client(
            api_base_url=conf.get('cli', 'endpoint_url'),
            auth=api.api_auth.client_auth)

        try:
            result = api_client.trigger_dag(dag_name)
        except Exception as e:
            result = "Sorry, but exception(%s) was raised during triggering your dag" % e

        msg.reply(result)
