# coding: utf-8

from opensource import licenses
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
