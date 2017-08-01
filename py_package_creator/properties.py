# coding: utf-8

from abc import ABCMeta, abstractmethod
from collections import OrderedDict
import getpass
from os import getcwd, path as Path
import re
import textwrap

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
        return Stringify.convert(self)

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

    INDENT_SIZE = 4

    __slots__ = '__indent'

    # def __init__(self, indent=None):
    #     assert indent is None or isinstance(indent, int)
    #
    #     self.__indent = indent
    #     self.__kwargs = None
    #
    # @property
    # def indent(self):
    #     return self.__indent


    @classmethod
    def boolean(cls, value, **kwargs):
        return str(value)

    @classmethod
    def convert(cls, value, **kwargs):
        descriptors = {
            bool: [cls.boolean],
            # bool: [str],
            int: [cls.number],
            float: [cls.number],
            str: [cls.string],
            tuple: [cls.list, 'indent'],
            list: [cls.list, 'indent'],
            dict: [cls.dict, 'indent', 'as_kwargs'],
            OrderedDict: [cls.dict, 'indent', 'as_kwargs']
        }

        tp = type(value)
        method_descriptor = descriptors.get(tp)

        if method_descriptor is None:
            raise ValueError('Unknown type {}'.format(tp))

        method = method_descriptor.pop(0)
        kw = {arg: kwargs.get(arg) for arg in method_descriptor}
        # print(kw)

        return method(value, **kwargs)
        # return method(value, **kw)

    @classmethod
    def dict(cls, value, indent=None, as_kwargs=False, **kwargs):
        def to_string(indent):
            indent = cls.INDENT_SIZE if indent is None else indent
            lines = ['{}: {}'.format(cls.convert(key, **kwargs), cls.convert(val, indent=indent, **kwargs))
                     for key, val in value.items()]
            return '{{\n{}\n}}'.format(cls.make_indent(lines, indent))

        def to_kwargs_string():
            lines = ['{}={}'.format(key, cls.convert(val, indent=indent, **kwargs)) for key, val in value.items()]
            return ', '.join(lines) if indent is None else cls.make_indent(lines, indent)

        return to_kwargs_string() if as_kwargs else to_string(indent)

    @classmethod
    def list(cls, value, indent=None, **kwargs):
        tp = type(value)
        value = tp(cls.convert(i, indent=indent, **kwargs) for i in value)

        if indent is None:
            pattern = '[{}]' if tp == list else '({})'
            return pattern.format(', '.join(value))

        pattern = '[\n{}\n]' if tp == list else '(\n{}\n)'
        return pattern.format(cls.make_indent(value, indent))

    @classmethod
    def make_indent(cls, value, indent=None):
        indent = indent or 0

        if isinstance(value, (list, tuple)):
            value = ',\n'.join(value)

        indent = ' ' * indent

        return textwrap.indent(value, indent)

    @classmethod
    def number(cls, value, **kwargs):
        return str(value)

    @classmethod
    def string(cls, value, **kwargs):
        return "'{}'".format(value)


class NameProperty(Property):
    """Name of the package"""

    __slots__ = ()

    def _get_default(self):
        return Path.basename(getcwd())

    def get_name(self):
        return 'name'

    def get_validator(self):
        return NotBlankValidator()


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
        if not self.get_default():
            return NotBlankValidator(), UrlValidator()
        return UrlValidator()


class AuthorProperty(Property):
    """Package author’s name"""

    __slots__ = ()

    def _get_default(self):
        return get_config_property('user.name') or getpass.getuser()

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


class DescriptionProperty(Property):
    """Short, summary description of the package"""

    __slots__ = ()

    def get_name(self):
        return 'description'
