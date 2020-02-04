import os
from subprocess import CalledProcessError, check_output


def run(command):
    print('$ '+command)
    output = check_output(command, shell=True).decode('ascii').strip()
    if output:
        print(output)
    return output


def version_not_tagged(remote='origin'):
    version = os.environ['TAG']
    if run('git remote -v'):
        run("git fetch {} 'refs/tags/*:refs/tags/*'".format(remote))
    try:
        run('git rev-parse --verify -q '+version)
    except CalledProcessError as e:
        if e.returncode == 1:
            print('No tag found.')
            return True
        raise
    else:
        print('Version is already tagged.')
        return False


def never():
    pass


def always():
    return True
