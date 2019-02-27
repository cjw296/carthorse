from os import chdir
from subprocess import check_output, STDOUT, CalledProcessError

import pytest
from testfixtures import TempDirectory, compare


@pytest.fixture()
def dir():
    with TempDirectory(encoding='ascii') as dir:
        chdir(dir.path)
        yield dir


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
        self.dir.write([repo, 'a'], 'some content')
        self.dir.write([repo, 'b'], 'other content')
        self.dir.write([repo, 'c'], 'more content')
        self('add .', repo)
        self('commit -m initial', repo)


@pytest.fixture()
def git(dir):
    return GitHelper(dir)
