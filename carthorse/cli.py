import os
from argparse import ArgumentParser
from datetime import datetime

from .config import load_config
from .plugins import Plugins


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--config', default='pyproject.toml')
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_config(args.config)
    plugins = Plugins.load()
    carthorse(config, plugins)


def carthorse(config, plugins):
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
        for action in config['actions']:
            config.run(plugins['actions'], action)
