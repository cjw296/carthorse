import os
import re
from pathlib import Path
from subprocess import check_output

import toml


def poetry():
    with open('pyproject.toml') as source:
        data = toml.load(source)
        return data['tool']['poetry']['version']


def setup_py(python='python'):
    return check_output([python, 'setup.py', '--version']).decode('ascii').strip()


def file(path, pattern='(?P<version>.*)'):
    with open(path) as source:
        match = re.search(pattern, source.read())
        if match is None:
            raise ValueError(f'{pattern} not found in {path}')
        try:
            version = match.group('version')
        except IndexError:
            raise ValueError(f"pattern {pattern} has no group named 'version'")
        return version.strip()


def flit(module):
    path = Path(module)
    if path.is_dir():
        path = str(path / '__init__.py')
    else:
        path = str(path) + '.py'
    return file(path, pattern=r'__version__\s*=\s*[\'"](?P<version>[^"\']+)')


def none():
    return ''


def env(variable='VERSION'):
    return os.environ[variable]
