from subprocess import call


def run(command):
    call(command, shell=True)
