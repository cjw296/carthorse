from unittest.mock import Mock, call

import toml
from testfixtures import Replacer, compare, ShouldRaise

from carthorse.cli import main


def test_run_through(dir):
    m = Mock()
    dir.write('pyproject.toml', toml.dumps({'tool': {'carthorse': {
        'version-from':
            {'name': 'dummy', 'version': '1.2.3'},
        'when': [
            {'name': 'dummy'},
        ],
        'actions': [
            {'dummy': 'action 1'},
            {'dummy': 'action 2'},
        ]
    }}}))
    with Replacer() as r:
        r.replace('carthorse.version_from.dummy', m.version_from, strict=False)
        m.version_from.return_value = '1.2.3'
        r.replace('carthorse.when.dummy', m.when, strict=False)
        r.replace('carthorse.actions.dummy', m.action, strict=False)
        r.replace('sys.argv', ['x'])
        main()
    compare(m.mock_calls, expected=[
        call.version_from(version='1.2.3'),
        call.when(version='1.2.3'),
        call.action('action 1', version='1.2.3'),
        call.action('action 2', version='1.2.3')
    ])


def test_when_stops(dir):
    m = Mock()
    dir.write('pyproject.toml', toml.dumps({'tool': {'carthorse': {
        'version-from':
            {'name': 'dummy'},
        'when': [
            {'name': 'dummy1'},
            {'name': 'dummy2'},
        ],
        'actions': [
            {'name': 'dummy'},
        ]
    }}}))
    with Replacer() as r:
        r.replace('carthorse.version_from.dummy', m.version_from, strict=False)
        m.version_from.return_value = '1.2.3'
        r.replace('carthorse.when.dummy1', m.when1, strict=False)
        m.when1.return_value = False
        r.replace('carthorse.when.dummy2', m.when2, strict=False)
        r.replace('carthorse.actions.dummy', m.action, strict=False)
        r.replace('sys.argv', ['x'])
        main()
    compare(m.mock_calls, expected=[
        call.version_from(),
        call.when1(version='1.2.3'),
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
        r.replace('carthorse.version_from.dummy', m.version_from, strict=False)
        m.version_from.return_value = '1.2.3'
        r.replace('carthorse.actions.dummy1', m.when1, strict=False)
        m.when1.side_effect = Exception('Boom!')
        r.replace('carthorse.actions.dummy2', m.when2, strict=False)
        r.replace('sys.argv', ['x'])
        with ShouldRaise(Exception('Boom!')):
            main()

    compare(m.mock_calls, expected=[
        call.version_from(),
        call.when1(version='1.2.3'),
    ])
