# coding: utf-8

from subprocess import check_output, CalledProcessError, DEVNULL, STDOUT
from os import getcwd
import re
import sys


def get_git_command():
    """Возвращает команду для вызова GIT-а."""
    return 'git'


def call_git(cmd, *args, cwd=None):
    """Выполнить git-команду с указанными аргументами."""

    args = [get_git_command(), cmd] + list(args)

    try:
        cwd = cwd or getcwd()
        """
        todo: stderr=DEVNULL replaced stderr=STDOUT
        https://stackoverflow.com/questions/13146187/git-unable-to-redirect-parse-the-output-of-git-fetch-dry-run-command
        """
        return check_output(args, stderr=STDOUT, cwd=cwd).decode(sys.stdout.encoding).strip()
    except CalledProcessError as e:
        print(e)
        return None


def get_config_property(prop):
    """Возвращает значение указанного конфигурационного параметра репозитория."""
    return call_git('config', '--get', prop)


class Repo(object):
    def __init__(self, folder):
        self.folder = folder

    def __call__(self, cmd, *args):
        return call_git(cmd, *args, cwd=self.folder)

    def get_branch_name(self):
        """Возвращает имя текущей ветки."""
        return self('rev-parse', '--abbrev-ref', 'HEAD')

    def get_remote_updates(self):
        """
        Возвращает изменения в удаленном репозитории, если таковые есть.

        Если изменения есть, то возвращается два списка.
        Первый список состоит из кортежей, где элементы кортежа это:
        - короткий хеш текущего локального коммита
        - короткий хеш последнего удаленного коммита
        - короткое название удаленного репозитория
        - имя ветки.

        Второй список состоит из кортежей новых веток, где элемента кортежа это:
        - короткое название удаленного репозитория
        - имя ветки.

        Если в удаленном репозитории нет изменений, то возвращается None.
        """

        response = self('fetch', '--dry-run')

        if not response:
            return None

        regexp_template = r'{}.+->\s+(.+)/(.+)'

        updates = re.findall(regexp_template.format(r'([0-9a-f]+)\.\.([0-9a-f]+)'), response, re.I)
        new_branches = re.findall(regexp_template.format(r'\[.+\]'), response, re.I)

        return updates, new_branches
