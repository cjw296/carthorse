import os
from subprocess import CalledProcessError

from testfixtures import Replace, compare, ShouldRaise, Replacer

from carthorse.when import never, always, version_not_tagged


class TestNever(object):

    def test_never(self):
        assert not never()


class TestAlways(object):

    def test_always(self):
        assert always()


class TestVersionNotTagged(object):

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
