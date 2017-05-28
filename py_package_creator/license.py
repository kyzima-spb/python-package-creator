# coding: utf-8

from opensource import licenses
from prompt_toolkit.completion import Completer, Completion
from requests import get as open_url

from py_package_creator.decorators import cached


@cached('classifiers.pickle')
def load_allowed_classifiers():
    """Возвращает список разрешенных PyPi классификаторов, описывающих лицензию."""

    url = 'https://pypi.python.org/pypi?%3Aaction=list_classifiers'
    response = open_url(url)
    return list(filter(lambda c: c.startswith('License :: '), response.text.split('\n')))


@cached('licenses.pickle')
def load_licenses():
    """Возвращает список лицензий, разрешенных к использованию на PyPi.org."""

    classifiers = load_allowed_classifiers()

    def cb(licence):
        for identifier in licence.identifiers:
            if identifier.get('scheme') == 'Trove':
                clf = identifier.get('identifier')
                return clf in classifiers

    return list(filter(cb, licenses.all()))


class LicenseCompleter(Completer):
    """Автодополнение для полей ввода."""

    def __init__(self):
        self.__licenses = load_licenses()

    def __get_matches(self, qs):
        for license in self.__licenses:
            lid = license.id.lower()
            name = license.name.lower()

            if lid.find(qs) != -1 or name.find(qs) != -1:
                yield license

    def get_completions(self, document, complete_event):
        word_before_cursor = document.text_before_cursor.lower()
        matches = self.__get_matches(word_before_cursor)

        for license in matches:
            yield Completion(license.id,
                             start_position=-len(word_before_cursor),
                             display=license.name)
