import os
from subprocess import CalledProcessError
from textwrap import dedent

from testfixtures import compare, Replace, ShouldRaise, Replacer

from carthorse.actions import run, create_tag
from carthorse.version_from import poetry, setup_py, flit, file, none, env
from carthorse.when import never, version_not_tagged, always


class TestVersionFrom(object):

    def test_poetry(self, dir):
        dir.write('pyproject.toml', dedent("""
        [tool.poetry]
        version = "0.1.0"
        """))
        compare(poetry(), expected='0.1.0')

    def test_setup_py(self, dir):
        dir.write('setup.py', dedent("""
        print('1.2.3')
        """))
        compare(setup_py(), expected='1.2.3')

    def test_file(self, dir):
        dir.write('package/version.txt', '1.2.3\n')
        compare(file('package/version.txt'), expected='1.2.3')

    def test_file_pattern_doesnt_match(self, dir):
        dir.write('package/version.txt', '1.2.3\n')
        with ShouldRaise(ValueError(r'\d{2} not found in package/version.txt')):
            file('package/version.txt', pattern=r'\d{2}')

    def test_file_pattern_has_no_group(self, dir):
        dir.write('package/version.txt', '1.2.3\n')
        with ShouldRaise(ValueError(r"pattern \d has no group named 'version'")):
            file('package/version.txt', pattern=r'\d')

    def test_flit_module(self, dir):
        dir.write('foobar.py', dedent('''
        """An amazing sample package!"""

        __version__ = '0.1'
        '''))
        compare(flit('foobar'), expected='0.1')

    def test_flit_package(self, dir):
        dir.write('foobar/__init__.py', dedent('''
        """An amazing sample package!"""

        __version__ = '0.1'
        '''))
        compare(flit('foobar'), expected='0.1')

    def test_none(self, dir):
        compare(none(), expected='')

    def test_env_default(self):
        with Replace('os.environ.VERSION', '1.2.3', strict=False):
            compare(env(), expected='1.2.3')

    def test_env_explicit_variable(self):
        with Replace('os.environ.MYVERSION', '1.2.3', strict=False):
            compare(env(variable='MYVERSION'), expected='1.2.3')


class TestWhenNever(object):

    def test_never(self):
        assert not never()


class TestWhenAlways(object):

    def test_always(self):
        assert always()


class TestWhenVersionNotTagged(object):

    def test_version_not_tagged(self, git, capfd):
        with Replace('os.environ.TAG', '1.2.3', strict=False):
            git.make_repo_with_content()
            os.chdir(git.dir.getpath(git.repo))

            assert version_not_tagged()

            out, err = capfd.readouterr()
            compare(out, expected=(
                '$ git remote -v\n'
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
                '$ git remote -v\n'
                '$ git rev-parse --verify -q v1.2.3\n'
                f'{rev}\n'
                'Version is already tagged.\n'
            ))
            compare(err, expected='')

    def test_not_in_git_repo(self, dir, capfd):
        with Replace('os.environ.TAG', 'v1.2.3', strict=False):
            with ShouldRaise(CalledProcessError):
                version_not_tagged()
        out, err = capfd.readouterr()
        compare(out, expected='$ git remote -v\n')
        compare(err.lower(),
                expected='fatal: not a git repository (or any of the parent directories): .git\n')

    def test_rev_parse_blows_up(self, dir):
        def run(command):
            if 'rev-parse' in command:
                raise CalledProcessError(42, command)
        with Replacer() as r:
            r.replace('os.environ.TAG', 'v1.2.3', strict=False)
            r.replace('carthorse.when.run', run)
            with ShouldRaise(CalledProcessError):
                version_not_tagged()

    def test_version_tagged_upstream(self, git, capfd):
        with Replace('os.environ.TAG', 'v1.2.3', strict=False):
            git.make_repo_with_content('remote')
            rev = git.rev_parse('HEAD', 'remote')
            git('clone remote local', git.dir.path)
            git('tag v1.2.3', 'remote')
            git.check_tags(repo='local', expected={})
            git.check_tags(repo='remote', expected={b'v1.2.3': rev})
            os.chdir(git.dir.getpath('local'))
            git.dir.write('local/a', 'changed')
            git('config user.email "test@example.com"')
            git('config user.name "Test User"')
            git("commit -am changed")

            assert not version_not_tagged()

            git.check_tags(repo='local', expected={b'v1.2.3': rev})
            git.check_tags(repo='remote', expected={b'v1.2.3': rev})

        out, _ = capfd.readouterr()
        compare(out, expected=(
            '$ git remote -v\n'
            f"{git('remote -v').decode('ascii')}"
            "$ git fetch origin 'refs/tags/*:refs/tags/*'\n"
            '$ git rev-parse --verify -q v1.2.3\n'
            f'{rev}\n'
            'Version is already tagged.\n'
        ))


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

    def test_exists_upstream(self, git, capfd):
        with Replace('os.environ.TAG', 'v1.2.3', strict=False):
            git.make_repo_with_content('remote')
            rev = git.rev_parse('HEAD', 'remote')
            git('clone remote local', git.dir.path)
            git('tag v1.2.3', 'remote')
            git.check_tags(repo='remote', expected={b'v1.2.3': rev})
            os.chdir(git.dir.getpath('local'))
            git.dir.write('local/a', 'changed')
            git('config user.email "test@example.com"')
            git('config user.name "Test User"')
            git("commit -am changed")

            with ShouldRaise(CalledProcessError) as s:
                create_tag()

            assert 'git push origin tag v1.2.3' in str(s.raised)
            git.check_tags(repo='remote', expected={b'v1.2.3': rev})

        capfd.readouterr()

    def test_exists_but_update(self, git, capfd):
        with Replace('os.environ.TAG', 'env-qa', strict=False):
            git.make_repo_with_content('remote')
            git('clone remote local', git.dir.path)
            git('tag env-qa', 'remote')
            git('tag env-qa')
            os.chdir(git.dir.getpath('local'))
            git.dir.write('local/a', 'changed')
            git('config user.email "test@example.com"')
            git('config user.name "Test User"')
            git("commit -am changed")
            rev = git.rev_parse('HEAD')

            create_tag(update=True)

            git.check_tags(repo='local', expected={b'env-qa': rev})
            git.check_tags(repo='remote', expected={b'env-qa': rev})

        capfd.readouterr()
