from subprocess import check_call


def run(command):
    print('$ '+command)
    check_call(command, shell=True)


def git_tag(format='v$VERSION', remote='origin'):
    run('git tag '+format)
    run('git push {} tag {}'.format(remote, format))
