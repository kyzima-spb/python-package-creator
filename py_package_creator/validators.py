# coding: utf-8

from __future__ import print_function
import re

from prompt_toolkit.validation import Validator, ValidationError


class ChainValidator(Validator):
    def __init__(self, validators=None):
        self.__validators = []

        for validator in validators:
            self.add_validator(validator)

    def add_validator(self, validator):
        if not isinstance(validator, Validator):
            raise RuntimeError('The passed argument is not a Validator')

        if validator not in self.__validators:
            self.__validators.append(validator)

    def validate(self, document):
        for validator in self.__validators:
            validator.validate(document)


class EmailValidator(Validator):
    def validate(self, document):
        email = document.text
        pattern = r'.+@.+'

        if email and not re.match(pattern, email, re.I):
            raise ValidationError(message='This value is not a valid email address')


class NotBlankValidator(Validator):
    def validate(self, document):
        if not document.text:
            raise ValidationError(message='This value should not be blank')


class UrlValidator(Validator):
    def validate(self, document):
        url = document.text
        pattern = r'^(http|ftp)s?://.+'

        if url and not re.match(pattern, url, re.I):
            raise ValidationError(message='This value is not a valid URL',
                                  cursor_position=len(url))
