import os
from subprocess import CalledProcessError
from textwrap import dedent

from testfixtures import compare, Replace, ShouldRaise

from carthorse.actions import run, create_tag
from carthorse.version_from import poetry
from carthorse.when import never, version_not_tagged


class TestVersionFrom(object):

    def test_poetry(self, dir):
        dir.write('pyproject.toml', dedent("""
        [tool.poetry]
        version = "0.1.0"
        """))
        compare(poetry(), expected='0.1.0')


class TestWhenNever(object):

    def test_never(self):
        assert not never()


class TestWhenVersionNotTagged(object):

    def test_version_not_tagged(self, git, capfd):
        with Replace('os.environ.TAG', '1.2.3', strict=False):
            git.make_repo_with_content()
            os.chdir(git.dir.getpath(git.repo))

            assert version_not_tagged()

            out, err = capfd.readouterr()
            compare(out, expected=(
                '$ git rev-parse --verify -q 1.2.3\n'
                'No tag found.\n'
            ))
            compare(err, expected='')

    def test_version_tagged(self, git, capfd):
        with Replace('os.environ.TAG', 'v1.2.3', strict=False):
            git.make_repo_with_content()
            git('tag v1.2.3')
            rev = git.rev_parse('HEAD')
            os.chdir(git.dir.getpath(git.repo))

            assert not version_not_tagged()

            out, err = capfd.readouterr()
            compare(out, expected=(
                '$ git rev-parse --verify -q v1.2.3\n'
                + rev +'\n'
            ))
            compare(err, expected='')

    def test_not_in_git_repo(self, dir, capfd):
        with Replace('os.environ.TAG', 'v1.2.3', strict=False):
            with ShouldRaise(CalledProcessError):
                version_not_tagged()
        out, err = capfd.readouterr()
        compare(out, expected='$ git rev-parse --verify -q v1.2.3\n')
        compare(err.lower(),
                expected='fatal: not a git repository (or any of the parent directories): .git\n')

    def test_version_tagged_upstream(self):
        assert not never()


class TestRun(object):

    def test_simple(self, capfd):
        run('echo hello')
        compare(capfd.readouterr().out, expected='$ echo hello\nhello\n')

    def test_env(self, capfd):
        with Replace('os.environ.GREETING', 'hello', strict=False):
            run('echo $GREETING')
            compare(capfd.readouterr().out, expected='$ echo $GREETING\nhello\n')

    def test_bad(self, capfd):
        with ShouldRaise(CalledProcessError):
            run('/dev/null')
        capfd.readouterr()


class TestCreateTag(object):

    def test_simple(self, git, capfd):
        with Replace('os.environ.TAG', 'v1.2.3', strict=False):
            git.make_repo_with_content('remote')
            git('clone remote local', git.dir.path)
            git.check_tags(repo='local', expected={})
            git.check_tags(repo='remote', expected={})
            rev = git.rev_parse('HEAD')
            os.chdir(git.dir.getpath('local'))

            create_tag()

            git.check_tags(repo='local', expected={b'v1.2.3': rev})
            git.check_tags(repo='remote', expected={b'v1.2.3': rev})
        capfd.readouterr()
