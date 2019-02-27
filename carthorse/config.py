from functools import reduce
from operator import __getitem__
from os.path import splitext

from yaml import safe_load as parse_yaml
from toml import load as parse_toml


class Config(object):

    def __init__(self, path):
        with open(path) as source:
            data = self.parse(source)
        self.data = reduce(__getitem__, self.root_key, data)
        self.data['version-from'] = self.expand(self.data['version-from'])
        for name in 'when', 'actions':
            self.data[name] = [self.expand(item) for item in self.data[name]]

    def expand(self, item):
        if isinstance(item, str):
            return dict(name=item, args=(), kw={})
        else:
            name = item.pop('name', None)
            if name is None:
                (name, arg),  = item.items()
            else:
                arg = item
            if isinstance(arg, dict):
                kw = arg
                args = ()
            else:
                kw = {}
                args = (arg,)
            return dict(name=name, args=args, kw=kw)

    def __getitem__(self, item):
        return self.data[item]

    def get(self, item, default):
        return self.data.get(item, default)

    def run(self, module, config):
        func = getattr(module, config['name'].replace('-', '_'))
        kw = config['kw'].copy()
        return func(*config['args'], **kw)


class TomlConfig(Config):
    root_key = ['tool', 'carthorse']

    def parse(self, source):
        return parse_toml(source)


class YamlConfig(Config):
    root_key = ['carthorse']

    def parse(self, source):
        return parse_yaml(source)


parsers = {
    '.toml': TomlConfig,
    '.yml': YamlConfig,
    '.yaml': YamlConfig,
}


def load_config(path):
    class_ = parsers[splitext(path)[-1]]
    return class_(path)
