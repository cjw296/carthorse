import os
import re
from subprocess import check_output


def run(command):
    print('$ '+command)
    output = check_output(command, shell=True).decode('ascii').strip()
    if output:
        print(output)
    return output


def create_tag(remote='origin', update=False):
    tag = os.environ['TAG']
    force = '--force ' if update else ''
    run(f"git tag {force}{tag}")
    run(f'git push {force}{remote} tag {tag}')


def update_major_tag(remote='origin', pattern='v[0-9]+'):
    env_tag = os.environ['TAG']
    match = re.match(pattern, env_tag)
    if match is None:
        raise ValueError(f"pattern {pattern!r} does not match {env_tag!r}")
    tag = match.group(0)
    run(f"git tag --force {tag}")
    run(f'git push --force {remote} tag {tag}')
