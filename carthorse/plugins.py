from collections import defaultdict

from importlib.metadata import entry_points


class Plugins(defaultdict):

    @classmethod
    def load(cls):
        """
        Load plugins from entrypoints specified in packages and register them
        """
        plugins = Plugins(dict)
        for type in 'version_from', 'when', 'actions':
            for entrypoint in entry_points(group='carthorse.'+type):
                plugin = entrypoint.load()
                plugins[type][entrypoint.name] = plugin
        return plugins
