import toml


def poetry():
    with open('pyproject.toml') as source:
        data = toml.load(source)
        return data['tool']['poetry']['version']
