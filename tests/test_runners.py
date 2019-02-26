from textwrap import dedent

from testfixtures import compare

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
        assert not never(version='why?')
