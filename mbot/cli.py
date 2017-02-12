# -*- coding: utf-8 -*-

import pprint

import click
from mbot import Bot
from mbot.config import Config


pp = pprint.PrettyPrinter()


@click.group()
def main(args=None, **kwargs):
    """Console script for mbot"""
    pass


def check_config(key):
    cfg = Config()
    cfg.load()
    return not cfg.is_ready(key)


@click.command()
@click.option('--state-path')
@click.option('--config-path')
@click.option('--encrypt', default=True)
@click.option('--slack-token', prompt=check_config("slack.token"))
def run(args=None, **kwargs):
    """Run mbot"""

    click.echo("Starting your BOT...")

    Bot(**kwargs).run()


@click.command()
def config(args=None, **kwargs):
    """Show config"""

    cfg = Config()
    cfg.load()
    pp.pprint(cfg.conf)


main.add_command(run)
main.add_command(config)

if __name__ == "__main__":
    main()
