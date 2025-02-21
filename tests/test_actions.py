import os
from subprocess import CalledProcessError

from testfixtures import compare, Replace, ShouldRaise

from carthorse.actions import run, create_tag


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
