from carthorse.plugins import Plugins


def test_load_plugins():
    plugins = Plugins.load()
    assert isinstance(plugins, dict)
    for name in 'version_from', 'when', 'actions':
        types = plugins[name]
        assert isinstance(types, dict)
        assert len(types) > 0
