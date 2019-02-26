from subprocess import CalledProcessError
from textwrap import dedent

from testfixtures import compare, Replace, ShouldRaise

from carthorse.actions import run
from carthorse.version_from import poetry
from carthorse.when import never


class TestVersionFrom(object):

    def test_poetry(self, dir):
        dir.write('pyproject.toml', dedent("""
        [tool.poetry]
        version = "0.1.0"
        """))
        compare(poetry(), expected='0.1.0')


class TestWhen(object):

    def test_never(self):
        assert not never()


class TestRun(object):

    def test_simple(self, capfd):
        run('echo hello')
        compare(capfd.readouterr().out, expected='hello\n')

    def test_env(self, capfd):
        with Replace('os.environ.GREETING', 'hello', strict=False):
            run('echo $GREETING')
            compare(capfd.readouterr().out, expected='hello\n')

    def test_bad(self, capfd):
        with ShouldRaise(CalledProcessError):
            run('/dev/null')
        capfd.readouterr()
