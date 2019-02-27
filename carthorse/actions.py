import os
from subprocess import check_call


def run(command):
    print('$ '+command)
    check_call(command, shell=True)


def git_tag(remote='origin'):
    tag = os.environ['TAG']
    run('git tag '+tag)
    run('git push {} tag {}'.format(remote, tag))
