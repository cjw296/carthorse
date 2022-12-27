import os
import re
from doctest import ELLIPSIS
from functools import partial, reduce
from operator import __getitem__
from os import chdir, getcwd
from pathlib import Path
from subprocess import check_output, STDOUT, CalledProcessError
from typing import Dict, Callable, cast, Sequence, Match

import pytest
from sybil import Sybil, Example
from sybil.parsers.rest import PythonCodeBlockParser, CodeBlockParser, DocTestParser
from testfixtures import TempDirectory, compare, Replace, OutputCapture
from toml import loads as parse_toml, dumps as serialize_toml
from yaml import safe_load as parse_yaml

from carthorse.cli import carthorse
from carthorse.config import Config, TomlConfig, YamlConfig
from carthorse.plugins import Plugins


@pytest.fixture()
def dir():
    with TempDirectory(encoding='ascii') as dir:
        current = getcwd()
        chdir(dir.path)
        try:
            yield dir
        finally:
            chdir(current)


class GitHelper(object):

    repo = 'local/'

    def __init__(self, dir):
        self.dir = dir

    def __call__(self, command, repo=None):
        repo_path = self.dir.getpath(repo or self.repo)
        try:
            return check_output(['git'] + command.split(), cwd=repo_path, stderr=STDOUT)
        except CalledProcessError as e:  # pragma: no cover
            raise RuntimeError('{0.cmd}: {0.output}'.format(e))

    def rev_parse(self, label, repo=None):
        return self('rev-parse --verify -q ' + label, repo).strip().decode('ascii')

    def check_tags(self, expected, repo=None):
        actual = {}
        for tag in self('tag', repo).split():
            actual[tag] = self.rev_parse(tag.decode(), repo)
        compare(expected, actual=actual)

    def make_repo_with_content(self, repo=None):
        repo = repo or self.repo
        self.dir.makedir(repo)
        self('init', repo)
        self('config user.email "test@example.com"', repo)
        self('config user.name "Test User"', repo)
        self.dir.write([repo, 'a'], 'some content')
        self.dir.write([repo, 'b'], 'other content')
        self.dir.write([repo, 'c'], 'more content')
        self('add .', repo)
        self('commit -m initial', repo)


@pytest.fixture()
def git(dir):
    return GitHelper(dir)


@pytest.fixture()
def repo(git: GitHelper) -> Path:
    git.make_repo_with_content('remote')
    git('clone remote local', git.dir.path)
    repo = git.dir.as_path('local')
    (repo / 'pyproject.toml').write_text(serialize_toml({'tool': {'poetry': {'version': '1.0'}}}))
    (repo / 'foobar.py').write_text('__version__="2.0"\n')
    (repo / 'setup.py').write_text('version="3.0"\n')
    os.chdir(repo)
    return repo


class ReadmeConfig(Config):

    def __init__(self, data: Dict, root_key: Sequence[str]):
        self.data = cast(Dict, reduce(__getitem__, root_key, data))
        self.data['version-from'] = self.expand(self.data.get('version-from', 'env'))
        for name, default in (
                ('when', 'always'),
                ('actions', {'run': 'echo $TAG'})
        ):
            value = self.data.get(name, [default])
            self.data[name] = [self.expand(item) for item in value]


def run_config(
        config: ReadmeConfig, *, expected_runs: Sequence = (), expected_phrases: Sequence = ()
):
    actual = []
    environ = {'VERSION': '4.0', 'MYVERSION': '5.0'}

    def envget(match: Match):
        return environ.get(match.group(1), '')

    def run(command):
        actual.append(re.sub(r'\$(\w+)', envget, command))

    plugins = Plugins.load()
    plugins['actions']['run'] = run
    with Replace('os.environ', environ), OutputCapture(fd=True) as output:
        carthorse(config, plugins)
    compare(actual, expected=expected_runs)
    assert not isinstance(expected_phrases, str)
    for phrase in expected_phrases:
        assert phrase in output.captured, f'{phrase!r} not in:\n{output.captured}'


def make_config(parse: Callable[[str], Dict], example: Example):
    root_key = TomlConfig.root_key if parse is parse_toml else YamlConfig.root_key
    config = ReadmeConfig(parse(example.parsed), root_key)
    example.namespace['run_config'] = partial(run_config, config)


pytest_collect_file = Sybil(
    parsers=[
        DocTestParser(optionflags=ELLIPSIS),
        PythonCodeBlockParser(),
        CodeBlockParser('toml', partial(make_config, parse_toml)),
        CodeBlockParser('yaml', partial(make_config, parse_yaml)),
    ],
    patterns=['*.rst'],
    fixtures=['repo']
).pytest()
