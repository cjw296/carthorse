from unittest.mock import Mock, call

from testfixtures import compare

from carthorse.config import load_config


EXPECTED_CONFIG = {
    'version-from':
        {'name': 'poetry', 'args': (), 'kw': {}},
    'tag-format': 'x{version}',
    'when': [
        {'name': 'version-not-tagged', 'args': (), 'kw': {}},
    ],
    'actions': [
        {'name': 'run',
         'args': ("poetry publish --username $POETRY_USER --password $POETRY_PASS --build",),
         'kw': {}},
        {'name': 'create-tag' , 'args': (), 'kw': {}},
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
          tag-format: x{version}
          when:
            - version-not-tagged
          actions:
            - run: "poetry publish --username $POETRY_USER --password $POETRY_PASS --build"
            - create-tag  
            - something-else
        """)
        config = load_config(path)
        compare(config.data, expected=EXPECTED_CONFIG)

    def test_parse_toml(self, dir):
        path = dir.write('test.toml', """
        [tool.carthorse]
        version-from = "poetry"
        tag-format = "x{version}"
        when = [
          "version-not-tagged"
        ]
        actions = [
           { run="poetry publish --username $POETRY_USER --password $POETRY_PASS --build"},
           { name="create-tag"},
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
        plugins = {'a-func': a_func}
        result = config.run(plugins, config['version-from'])
        compare(result, expected=(1, 2, 3))
