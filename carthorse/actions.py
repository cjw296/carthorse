import os
import re
from subprocess import check_output, CalledProcessError, STDOUT


def run(command):
    print('$ '+command)
    returncode = None
    try:
        output = check_output(command, shell=True, stderr=STDOUT)
    except CalledProcessError as e:
        output = e.output
        returncode = e.returncode
    if returncode is not None:
        print(f'returncode={returncode}')
    text = output.decode()
    if text:
        print(text, end='')
    if returncode is not None:
        raise SystemExit(returncode)
    return text.strip()


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
