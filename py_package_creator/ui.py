# coding: utf-8

"""
Элементы ввода.
"""

from abc import ABCMeta, abstractmethod

from prompt_toolkit.shortcuts import prompt, print_tokens, create_confirm_application, run_application
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.filters import Condition
from prompt_toolkit.key_binding.manager import KeyBindingManager
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import style_from_dict
from pygments.token import Token

from .validators import ChainValidator


class Input(metaclass=ABCMeta):
    """Базовый элемент ввода."""

    def __init__(self, message, default=None):
        """
        Arguments:
            message (str): подсказка для ввода.
            default (mixed): значение по-умолчанию.
        """

        assert isinstance(message, str)

        self.__message = message
        self.__default = default

    def _get_prompt_style(self):
        """Возвращает стилевое оформление подсказки ввода."""

        return style_from_dict({
            Token: '#ansiwhite',
            Token.Message: '#ansiwhite bold',
            Token.Default: '#ansibrown',
            Token.Pound: '#ansiwhite bold'
        })

    def _get_prompt_tokens(self, cli=None):
        """Возвращает составляющие подсказки ввода."""

        return [
            (Token.Message, '{}'.format(self.get_message())),
            (Token.Pound, ': ')
        ]

    @abstractmethod
    def execute(self):
        """Запрашивает данные от пользователя и возвращает результат."""
        pass

    def get_default(self):
        """Возвращает значение по-умолчанию."""
        return self.__default

    def get_message(self):
        """Возвращает сообщение или другими словами подсказку для ввода."""
        return self.__message


class Prompt(Input):
    def __init__(self, message, default='', validator=None, **kwargs):
        assert isinstance(default, str)

        super(Prompt, self).__init__(message, default)

        self.__validator = validator
        self.kwargs = kwargs

    def _get_prompt_kwargs(self):
        kwargs = {}
        kwargs.update(self.kwargs)

        manager = KeyBindingManager.for_prompt()

        @manager.registry.add_binding(Keys.Enter, filter=Condition(lambda cli: cli.buffers[DEFAULT_BUFFER].text == ''))
        def _(event):
            event.cli.buffers[DEFAULT_BUFFER].text = self.get_default()
            event.cli.set_return_value(self.get_default())

        kwargs['key_bindings_registry'] = manager.registry

        validator = self.get_validator()

        if validator is not None:
            kwargs['validator'] = validator

        return kwargs

    def _get_prompt_tokens(self, cli=None):
        tokens = super(Prompt, self)._get_prompt_tokens(cli)

        dflt = self.get_default()

        if dflt is not None or dflt == '':
            tokens.insert(1, (Token.Default, ' ({})'.format(dflt)))

        return tokens

    def execute(self):
        return prompt(get_prompt_tokens=self._get_prompt_tokens,
                      style=self._get_prompt_style(),
                      **self._get_prompt_kwargs())

    def get_validator(self):
        """Возвращает валидатор или цепочку валидаторов"""
        return self.__validator

    def set_validator(self, validator):
        """Заменяет существующий валидатор или цепочку валидаторов"""

        if isinstance(validator, (list, tuple)):
            validator = ChainValidator(validator)

        self.__validator = validator


class Confirm(Input):
    def __init__(self, message, default=True):
        assert isinstance(default, bool)
        super(Confirm, self).__init__(message, default)

    def _get_prompt_tokens(self, cli=None):
        tokens = super(Confirm, self)._get_prompt_tokens(cli)

        dflt = 'Y/n' if self.get_default() else 'y/N'
        tokens.insert(1, (Token.Default, ' ({})'.format(dflt)))

        return tokens

    def execute(self):
        print_tokens(self._get_prompt_tokens(), style=self._get_prompt_style())

        app = create_confirm_application('')

        @app.key_bindings_registry.add_binding(Keys.Enter)
        def _(event):
            event.cli.buffers[DEFAULT_BUFFER].text = 'Y' if self.get_default() else 'N'
            event.cli.set_return_value(self.get_default())

        return run_application(app)
