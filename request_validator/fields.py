

import copy

from .validator import *


class Field(object):
    def __init__(self, source=None, required=False, many=False, default=None):
        self._source = source
        self._data = None
        self.data = None
        self._many = many
        self._errors = []
        self._rules = {}
        self._required = required
        self._default = default

    def set_data(self, data, index):
        self.data = self._default
        self._errors = []

        self._data = data

        if not self._data:
            if self._required:
                self._errors.append("This field is required")
            return self

        if self._source is not None and self._source in self._data:
            self.data = self._data[self._source]
        elif index in self._data:
            self.data = self._data[index]
        else:
            if self._required:
                self._errors.append("This field is required")

        return self

    def is_required(self):
        return self._required

    def add_rule(self, rule, value=None):
        self._rules[rule] = value

    def data(self):
        return self.data

    def get_errors(self):
        return self._errors

    def has_error(self):
        return len(self._errors) != 0

    def validate(self):
        if not self._many:
            for rule, value in self._rules.items():
                validator = Validator(self.data, rule, value)
                if validator.validate():
                    self.data = validator.data
                    continue
                else:
                    self._errors.append(validator.get_message())
        else:
            assert isinstance(self.data, list) or isinstance(self.data, tuple), \
                """ data must be list or tuple but get {data_type}""".format(
                    data_type=type(self.data).__name__)
            for data in self.data:
                for rule, value in self._rules.items():
                    validator = Validator(data, rule, value)
                    if validator.validate():
                        continue
                    else:
                        self._errors.append(validator.get_message())
        return not self.has_error()


class CharField(Field):
    def __init__(self, min_length=None, max_length=None, choices=None, allow_blank=False, allow_null=True, *args,
                 **kwargs):
        super(CharField, self).__init__(*args, **kwargs)

        self.add_rule(Validator.STRING)

        if not allow_blank:
            self.add_rule(Validator.NOT_BLANK)
        if not allow_null:
            self.add_rule(Validator.NOT_NULL)

        if min_length is not None:
            assert isinstance(min_length, int), \
                """min_length must be integer"""
            self.add_rule(Validator.MIN_LEN, min_length)

        if max_length is not None:
            assert isinstance(max_length, int), \
                """max_length must be integer"""
            self.add_rule(Validator.MAX_LEN, max_length)

        if choices is not None:
            assert isinstance(choices, list) or isinstance(choices, tuple), \
                """choices must be tuple or list"""
            self.add_rule(Validator.IN, choices)


class IntField(Field):
    def __init__(self, min_value=None, max_value=None, choices=None, allow_null=True, *args,
                 **kwargs):
        super(IntField, self).__init__(*args, **kwargs)

        self.add_rule(Validator.INT)

        if not allow_null:
            self.add_rule(Validator.NOT_NULL)

        if min_value is not None:
            assert isinstance(min_value, int), \
                """min_value must be integer"""
            self.add_rule(Validator.MIN_VALUE, min_value)

        if max_value is not None:
            assert isinstance(max_value, int), \
                """max_length must be integer"""
            self.add_rule(Validator.MAX_LEN, max_value)

        if choices is not None:
            assert isinstance(choices, list) or isinstance(choices, tuple), \
                """choices must be tuple or list"""
            for choice in choices:
                assert isinstance(choice, int), \
                    """
                    choices must be list or tuple of integer but get {data_type}
                    """.format(data_type=type(choice).__name_)
            self.add_rule(Validator.IN, choices)


class IntegerField(IntField):
    pass


class FloatField(Field):
    def __init__(self, min_value=None, max_value=None, choices=None, allow_null=True, *args,
                 **kwargs):
        super(FloatField, self).__init__(*args, **kwargs)

        self.add_rule(Validator.FLOAT)

        if not allow_null:
            self.add_rule(Validator.NOT_NULL)

        if min_value is not None:
            assert isinstance(min_value, float), \
                """min_value must be integer"""
            self.add_rule(Validator.MIN_VALUE, min_value)

        if max_value is not None:
            assert isinstance(max_value, float), \
                """max_length must be integer"""
            self.add_rule(Validator.MAX_LEN, max_value)

        if choices is not None:
            assert isinstance(choices, list) or isinstance(choices, tuple), \
                """choices must be tuple or list"""
            for choice in choices:
                assert isinstance(choice, float), \
                    """
                    choices must be list or tuple of integer but get {data_type}
                    """.format(data_type=type(choice).__name_)
            self.add_rule(Validator.IN, choices)


class RegexField(CharField):
    def __init__(self, pattern, *args, **kwargs):
        super(RegexField, self).__init__(*args, **kwargs)

        self.add_rule(Validator.REGEX, pattern)


class DateField(Field):
    def __init__(self, format=None, convert_to_date=False, *args, **kwargs):
        super(DateField, self).__init__(*args, **kwargs)
        if format:
            self._format = format
        else:
            self._format = "%Y-%m-%d"

        self.add_rule(Validator.DATE, {"format": self._format, "convert_to_date": convert_to_date})


class DateTimeField(Field):
    def __init__(self, format=None, convert_to_datetime=False, *args, **kwargs):
        super(DateTimeField, self).__init__(*args, **kwargs)
        if format:
            self._format = format
        else:
            self._format = "%Y-%m-%dT%H:%M:%S"

        self.add_rule(Validator.DATETIME, {"format": self._format, "convert_to_datetime": convert_to_datetime})


class BooleanField(Field):
    def __init__(self, *args, **kwargs):
        super(BooleanField, self).__init__(*args, **kwargs)
        self.add_rule(Validator.BOOLEAN)