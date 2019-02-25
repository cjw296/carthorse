from textwrap import dedent

import pytest
from testfixtures import TempDirectory, compare

from carthorse.config import load_config


@pytest.fixture()
def dir():
    with TempDirectory(encoding='ascii') as dir:
        yield dir


def write(dir, filename, text):
    return dir.write(filename, dedent(text))


EXPECTED_CONFIG = {
    'version-from':
        {'name': 'poetry', 'args': (), 'kw': {}},
    'when': [
        {'name': 'version-not-tagged', 'args': (), 'kw': {}},
    ],
    'actions': [
        {'name': 'run',
         'args': ("poetry publish --username $POETRY_USER --password $POETRY_PASS --build",),
         'kw': {}},
        {'name': 'git-tag' , 'args': (), 'kw': {'format': 'v$VERSION'}},
        {'name': 'something-else', 'args': (), 'kw': {}},
    ]
}


def a_func(a, b, c):
    return a, b, c


class TestConfig(object):

    def test_parse_yaml(self, dir):
        path = dir.write('test.yaml', """
        carthorse:
          version-from: poetry
          when:
            - version-not-tagged
          actions:
            - run: "poetry publish --username $POETRY_USER --password $POETRY_PASS --build"
            - git-tag:
                format: v$VERSION 
            - something-else
        """)
        config = load_config(path)
        compare(config.data, expected=EXPECTED_CONFIG)

    def test_parse_toml(self, dir):
        path = dir.write('test.toml', """
        [tool.carthorse]
        version-from = "poetry"
        when = [
          "version-not-tagged"
        ]
        actions = [
           { run="poetry publish --username $POETRY_USER --password $POETRY_PASS --build"},
           { name="git-tag", format="v$VERSION" },
           { name="something-else"}
        ]
        """)
        config = load_config(path)
        compare(config.data, expected=EXPECTED_CONFIG)

    def test_run(self, dir):
        path = dir.write('test.toml', """
        [tool.carthorse]
        version-from = { name="a-func", a=1, b=2, c=3 }
        when = []
        actions = []
        """)
        config = load_config(path)
        from . import test_config
        result = config.run(test_config, config['version-from'])
        compare(result, expected=(1, 2, 3))
