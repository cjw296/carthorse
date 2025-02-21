from textwrap import dedent

from testfixtures import compare, ShouldRaise, Replace

from carthorse.version_from import poetry, setup_py, file, flit, none, env


def test_poetry(dir):
    dir.write('pyproject.toml', dedent("""
    [tool.poetry]
    version = "0.1.0"
    """))
    compare(poetry(), expected='0.1.0')

def test_setup_py(dir):
    dir.write('setup.py', dedent("""
    print('1.2.3')
    """))
    compare(setup_py(), expected='1.2.3')

def test_file(dir):
    dir.write('package/version.txt', '1.2.3\n')
    compare(file('package/version.txt'), expected='1.2.3')

def test_file_pattern_doesnt_match(dir):
    dir.write('package/version.txt', '1.2.3\n')
    with ShouldRaise(ValueError(r'\d{2} not found in package/version.txt')):
        file('package/version.txt', pattern=r'\d{2}')

def test_file_pattern_has_no_group(dir):
    dir.write('package/version.txt', '1.2.3\n')
    with ShouldRaise(ValueError(r"pattern \d has no group named 'version'")):
        file('package/version.txt', pattern=r'\d')

def test_flit_module(dir):
    dir.write('foobar.py', dedent('''
    """An amazing sample package!"""

    __version__ = '0.1'
    '''))
    compare(flit('foobar'), expected='0.1')

def test_flit_package(dir):
    dir.write('foobar/__init__.py', dedent('''
    """An amazing sample package!"""

    __version__ = '0.1'
    '''))
    compare(flit('foobar'), expected='0.1')

def test_none(dir):
    compare(none(), expected='')

def test_env_default():
    with Replace('os.environ.VERSION', '1.2.3', strict=False):
        compare(env(), expected='1.2.3')

def test_env_explicit_variable():
    with Replace('os.environ.MYVERSION', '1.2.3', strict=False):
        compare(env(variable='MYVERSION'), expected='1.2.3')
