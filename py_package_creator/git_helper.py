# coding: utf-8

from subprocess import check_output, CalledProcessError, DEVNULL
from os import getcwd


def get_git_command():
    """Возвращает команду для вызова GIT-а."""
    return 'git'


def get_config_property(prop):
    """Возвращает значение указанного конфигурационного параметра репозитория."""

    try:
        args = [get_git_command(), 'config', '--get', prop]
        return check_output(args, stderr=DEVNULL, cwd=getcwd()).decode('ascii').strip()
    except CalledProcessError:
        return None
