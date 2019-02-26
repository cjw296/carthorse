from subprocess import call


def run(command, version=None):
    call(command, shell=True)
