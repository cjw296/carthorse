import os
from subprocess import CalledProcessError

from testfixtures import compare, Replace, ShouldRaise

from carthorse.actions import run, create_tag, update_major_tag


class TestRun(object):

    def test_simple(self, capfd):
        run('echo hello')
        compare(capfd.readouterr().out, expected='$ echo hello\nhello\n')

    def test_env(self, capfd):
        with Replace('os.environ.GREETING', 'hello', strict=False):
            run('echo $GREETING')
            compare(capfd.readouterr().out, expected='$ echo $GREETING\nhello\n')

    def test_bad(self, capfd):
        with ShouldRaise(SystemExit(126)):
            run('/dev/null')
        compare(
            capfd.readouterr().out,
            expected=(
                '$ /dev/null\n'
                'returncode=126\n'
            ),
        )

    def test_failure_with_output(self, capfd):
        with ShouldRaise(SystemExit(32)):
            run('echo "some stuff" && exit 32')
        compare(
            capfd.readouterr().out,
            expected=(
                '$ echo "some stuff" && exit 32\n'
                'returncode=32\n'
                'some stuff\n'
            ),
        )

    def test_non_ascii_output(self, capfd):
        run('echo "100% ━━━━━━━━━ 20.5/20.5 kB • 00:00 • 26.5 MB/s"')
        compare(
            capfd.readouterr().out,
            expected=(
                '$ echo "100% ━━━━━━━━━ 20.5/20.5 kB • 00:00 • 26.5 MB/s"\n'
                '100% ━━━━━━━━━ 20.5/20.5 kB • 00:00 • 26.5 MB/s\n'
            ),
        )


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

            with ShouldRaise(SystemExit) as s:
                create_tag()

            assert 'git push origin tag v1.2.3' in str(capfd.readouterr())
            git.check_tags(repo='remote', expected={b'v1.2.3': rev})

        capfd.readouterr()

    def test_exists_but_update(self, git, capfd):
        with Replace('os.environ.TAG', 'env-qa', strict=False):
            git.make_repo_with_content('remote')
            git('clone remote local', git.dir.path)
            git('tag env-qa', 'remote')
            git('tag env-qa')
            old_rev = git.rev_parse('HEAD')
            os.chdir(git.dir.getpath('local'))
            git.dir.write('local/a', 'changed')
            git('config user.email "test@example.com"')
            git('config user.name "Test User"')
            git("commit -am changed")
            new_rev = git.rev_parse('HEAD')
            assert new_rev != old_rev

            create_tag(update=True)

            git.check_tags(repo='local', expected={b'env-qa': new_rev})
            git.check_tags(repo='remote', expected={b'env-qa': new_rev})

        capfd.readouterr()



class TestUpdateMajorTag(object):

    def test_does_not_exist(self, git, capfd):
        with Replace('os.environ.TAG', 'v1.2.3', strict=False):
            git.make_repo_with_content('remote')
            git('clone remote local', git.dir.path)
            git.check_tags(repo='local', expected={})
            git.check_tags(repo='remote', expected={})
            rev = git.rev_parse('HEAD')
            os.chdir(git.dir.getpath('local'))

            update_major_tag()

            git.check_tags(repo='local', expected={b'v1': rev})
            git.check_tags(repo='remote', expected={b'v1': rev})
        capfd.readouterr()

    def test_exists_not_up_to_date(self, git, capfd):
        with Replace('os.environ.TAG', 'v1.2.3', strict=False):
            git.make_repo_with_content('remote')
            old_rev = git.rev_parse('HEAD', 'remote')
            git('clone remote local', git.dir.path)
            git('tag v1', 'remote')
            git.check_tags(repo='remote', expected={b'v1': old_rev})
            os.chdir(git.dir.getpath('local'))
            git.dir.write('local/a', 'changed')
            git('config user.email "test@example.com"')
            git('config user.name "Test User"')
            git("commit -am changed")
            new_rev = git.rev_parse('HEAD')
            assert new_rev != old_rev
            os.chdir(git.dir.getpath('local'))

            update_major_tag()

            git.check_tags(repo='local', expected={b'v1': new_rev})
            git.check_tags(repo='remote', expected={b'v1': new_rev})
        capfd.readouterr()

    def test_exists_up_to_date(self, git, capfd):
        with Replace('os.environ.TAG', 'v1.2.3', strict=False):
            git.make_repo_with_content('remote')
            rev = git.rev_parse('HEAD', 'remote')
            git('clone remote local', git.dir.path)
            git('tag v1', 'remote')
            git.check_tags(repo='remote', expected={b'v1': rev})
            os.chdir(git.dir.getpath('local'))

            update_major_tag()

            git.check_tags(repo='local', expected={b'v1': rev})
            git.check_tags(repo='remote', expected={b'v1': rev})
        capfd.readouterr()

    def test_custom_pattern(self, git, capfd):
        with Replace('os.environ.TAG', '1.2.3', strict=False):
            git.make_repo_with_content('remote')
            git('clone remote local', git.dir.path)
            git.check_tags(repo='local', expected={})
            git.check_tags(repo='remote', expected={})
            rev = git.rev_parse('HEAD')
            os.chdir(git.dir.getpath('local'))

            update_major_tag(pattern=r'1\.[0-9]+')

            git.check_tags(repo='local', expected={b'1.2': rev})
            git.check_tags(repo='remote', expected={b'1.2': rev})
        capfd.readouterr()

    def test_pattern_not_found_in_tag(self, git, capfd):
        with Replace('os.environ.TAG', '1.2.3', strict=False):
            git.make_repo_with_content('remote')
            git('clone remote local', git.dir.path)
            git.check_tags(repo='local', expected={})
            git.check_tags(repo='remote', expected={})
            rev = git.rev_parse('HEAD')
            os.chdir(git.dir.getpath('local'))

            with ShouldRaise(ValueError("pattern 'v[0-9]+' does not match '1.2.3'")):
                update_major_tag()

            git.check_tags(repo='local', expected={})
            git.check_tags(repo='remote', expected={})
        capfd.readouterr()
