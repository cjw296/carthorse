from unittest.mock import Mock, call

import toml
from coverage.annotate import os
from testfixtures import Replacer, compare, ShouldRaise, not_there

from carthorse.cli import main
from carthorse.when import never


def test_run_through(dir):
    m = Mock()
    dir.write('pyproject.toml', toml.dumps({'tool': {'carthorse': {
        'version-from':
            {'name': 'dummy', 'param': 'value'},
        'when': [
            {'name': 'dummy'},
        ],
        'actions': [
            {'dummy': 'action 1'},
            {'dummy': 'action 2'},
        ]
    }}}))
    with Replacer() as r:
        r.replace('carthorse.plugins.Plugins.load', lambda *args: {
            'version_from': {'dummy': m.version_from},
            'when': {'dummy': m.when},
            'actions': {'dummy': m.action},
        })
        m.version_from.return_value = '1.2.3'
        r.replace('sys.argv', ['x'])
        main()
    compare(m.mock_calls, expected=[
        call.version_from(param='value'),
        call.when(),
        call.action('action 1', ),
        call.action('action 2', )
    ])


def test_when_stops(dir):
    m = Mock()
    dir.write('pyproject.toml', toml.dumps({'tool': {'carthorse': {
        'version-from':
            {'name': 'dummy'},
        'when': [
            {'name': 'never'},
            {'name': 'dummy'},
        ],
        'actions': [
            {'name': 'dummy'},
        ]
    }}}))
    with Replacer() as r:
        r.replace('carthorse.plugins.Plugins.load', lambda *args: {
            'version_from': {'dummy': m.version_from},
            'when': {'dummy': m.when, 'never': never},
            'actions': {'dummy': m.action},
        })
        m.version_from.return_value = '1.2.3'
        r.replace('sys.argv', ['x'])
        main()
    compare(m.mock_calls, expected=[
        call.version_from(),
    ])


def test_exception_during_action(dir):
    m = Mock()
    dir.write('pyproject.toml', toml.dumps({'tool': {'carthorse': {
        'version-from':
            {'name': 'dummy'},
        'when': [],
        'actions': [
            {'name': 'dummy1'},
            {'name': 'dummy2'},
        ]
    }}}))
    with Replacer() as r:
        r.replace('carthorse.plugins.Plugins.load', lambda *args: {
            'version_from': {'dummy': m.version_from},
            'actions': {'dummy1': m.action1, 'dummy2': m.action2},
        })
        m.version_from.return_value = '1.2.3'
        m.action1.side_effect = Exception('Boom!')
        r.replace('sys.argv', ['x'])
        with ShouldRaise(Exception('Boom!')):
            main()

    compare(m.mock_calls, expected=[
        call.version_from(),
        call.action1(),
    ])


def check_tag_from_env(dir, config, expected):
    tags_seen = []
    def record_tag():
        tags_seen.append(os.environ.get('TAG'))
        return True
    m = Mock()
    dir.write('pyproject.toml', toml.dumps(config))
    with Replacer() as r:
        r.replace('carthorse.plugins.Plugins.load', lambda *args: {
            'version_from': {'dummy': m.version_from},
            'when': {'dummy': record_tag},
            'actions': {'dummy': record_tag},
        })
        m.version_from.return_value = '1.2.3'
        r.replace('sys.argv', ['x'])
        r.replace('sys.environ.TAG', not_there, strict=False)
        main()
    compare(tags_seen, expected=expected)


def test_tag_from_env(dir):
    check_tag_from_env(
        dir,
        config={'tool': {'carthorse': {
            'version-from':
                {'name': 'dummy'},
            'when': [
                {'name': 'dummy'},
            ],
            'actions': [
                {'name': 'dummy'},
            ]
        }}},
        expected=[
            'v1.2.3',
            'v1.2.3',
        ])


def test_tag_format_specified(dir):
    check_tag_from_env(
        dir,
        config={'tool': {'carthorse': {
            'version-from':
                {'name': 'dummy'},
            'tag-format': 'x-{version}-y',
            'when': [
                {'name': 'dummy'},
            ],
            'actions': [
                {'name': 'dummy'},
            ]
        }}},
        expected=[
            'x-1.2.3-y',
            'x-1.2.3-y',
        ])
