import os
from subprocess import check_call


def run(command):
    print('$ '+command)
    check_call(command, shell=True)


def create_tag(remote='origin', update=False):
    tag = os.environ['TAG']
    force = '--force ' if update else ''
    run(f"git tag {force}{tag}")
    run(f'git push {force}{remote} tag {tag}')
