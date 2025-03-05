from testfixtures import compare

from carthorse.plugins import Plugins


def test_load_plugins():
    plugins = Plugins.load()
    actual = {}
    for type_, type_plugins in plugins.items():
        actual[type_] = plugin_names = []
        for name, plugin in type_plugins.items():
            assert callable(plugin)
            plugin_names.append(name)
        plugin_names.sort()

    compare(actual, expected={
        'version_from': ['env', 'file', 'flit', 'none', 'poetry', 'pyproject', 'setup.py'],
        'when': ['always', 'never', 'version-not-tagged'],
        'actions': ['create-tag', 'run', 'update-major-tag'],
    })
