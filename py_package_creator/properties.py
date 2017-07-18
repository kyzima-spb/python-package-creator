# coding: utf-8

from abc import ABCMeta, abstractmethod
from os import getcwd, path as Path
import re

from six import with_metaclass

from .git_helper import get_config_property
from .license import LicenseCompleter
from .ui import Prompt, Confirm
from .validators import NotBlankValidator, UrlValidator


class Property(with_metaclass(ABCMeta, object)):
    """
    Класс для получения значения свойства пакета.
    """

    __slots__ = '_default', '_value'

    def __init__(self):
        self._value = None

    def __str__(self):
        return Stringify.string(self)

    def _get_default(self):
        """Возвращает не кешированное значение по-умолчанию."""
        return ''

    def _get_input_object(self):
        """Возвращает элемент ввода."""
        return Prompt(message=self.get_name(),
                      default=self.get_default(),
                      validator=self.get_validator())

    def execute(self):
        """Запрашивает значение свойства от пользователя и возвращает результат."""
        self._value = self._get_input_object().execute()

    def get_default(self):
        """Возвращает значение по-умолчанию."""

        if not hasattr(self, '_default'):
            setattr(self, '_default', self._get_default())

        return getattr(self, '_default')

    @abstractmethod
    def get_name(self):
        """Возвращает имя свойства."""
        pass

    def get_validator(self):
        """Возвращает валидатор или цепочку валидаторов."""
        return None

    def get_value(self):
        return self._value


class Stringify(object):
    """Конвертер свойств в строку."""

    __slots__ = () # dict

    @classmethod
    def execute(cls, prop, callback):
        assert isinstance(prop, Property)
        return '{}={}'.format(prop.get_name(), callback(prop.get_value()))

    @classmethod
    def boolean(cls, prop):
        return cls.execute(prop, lambda value: 'True' if value else 'False')

    @classmethod
    def list(cls, prop):
        return cls.execute(prop, lambda value: '[{}]'.format(', '.join(value)))

    @classmethod
    def number(cls, prop):
        return cls.execute(prop, lambda value: '{}'.format(value))

    @classmethod
    def string(cls, prop):
        return cls.execute(prop, lambda value: '"{}"'.format(value))


class NameProperty(Property):
    """Name of the package"""

    __slots__ = ()

    def __str__(self):
        return Stringify.list(self)

    def _get_default(self):
        return Path.basename(getcwd())

    def get_name(self):
        return 'name'


class UrlProperty(Property):
    """Home page for the package."""

    __slots__ = ()

    def _get_default(self):
        url = get_config_property('remote.origin.url')

        if url is None:
            return None

        pattern = r'(.+?)://.+?@(.+?)'
        repl = r'\1://\2'
        url = re.sub(pattern, repl, url)

        pattern = r'.+?(github.com|bitbucket.org|gitlab.com)(:|/)(.+?)\.git'
        repl = r'https://\1/\3'
        url = re.sub(pattern, repl, url)

        return url

    def get_name(self):
        return 'url'

    def get_validator(self):
        if self.get_default() is None:
            return NotBlankValidator(), UrlValidator()
        return UrlValidator()


class AuthorProperty(Property):
    """Package author’s name"""

    __slots__ = ()

    def _get_default(self):
        return get_config_property('user.name')

    def get_name(self):
        return 'author'


class AuthorEmailProperty(Property):
    """Email address of the package author"""

    __slots__ = ()

    def _get_default(self):
        return get_config_property('user.email')

    def get_name(self):
        return 'author_email'


class LicenseProperty(Property):
    """license for the package"""

    __slots__ = ()

    def _get_input_object(self):
        p = super(LicenseProperty, self)._get_input_object()
        p.kwargs['completer'] = LicenseCompleter()
        return p

    def get_name(self):
        return 'license'
