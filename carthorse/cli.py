import os
from argparse import ArgumentParser
from datetime import datetime

from .config import load_config
from .plugins import Plugins
from . import actions


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--config', default='pyproject.toml')
    parser.add_argument('--dry-run', action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config(args.config)
    plugins = Plugins.load()
    carthorse(config, plugins, args.dry_run)


def carthorse(config, plugins, dry_run):
    version = config.run(plugins['version_from'], config['version-from'])
    tag_format = config.get('tag-format', 'v{version}')
    os.environ['TAG'] = tag_format.format(
        now=datetime.now(),
        version=version,
    )
    ok = True
    for check in config['when']:
        ok = config.run(plugins['when'], check)
        if not ok:
            break
    if ok:
        if dry_run:
            actions.check_output = lambda *_, **__: b''
        for action in config['actions']:
            config.run(plugins['actions'], action)
