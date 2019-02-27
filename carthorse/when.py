import os
from subprocess import CalledProcessError, check_output


def version_not_tagged():
    version = os.environ['TAG']
    command = 'git rev-parse --verify -q '+version
    print('$ '+command)
    try:
        tag = check_output(command, shell=True).decode('ascii').strip()
    except CalledProcessError as e:
        if e.returncode == 1:
            print('No tag found.')
            return True
        raise
    else:
        print(tag)
        return False


def never():
    pass
