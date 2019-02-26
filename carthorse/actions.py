from subprocess import check_call


def run(command):
    check_call(command, shell=True)
