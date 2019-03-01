from subprocess import check_output

import toml


def poetry():
    with open('pyproject.toml') as source:
        data = toml.load(source)
        return data['tool']['poetry']['version']


def setup_py(python='python'):
    return check_output([python, 'setup.py', '--version']).decode('ascii').strip()
