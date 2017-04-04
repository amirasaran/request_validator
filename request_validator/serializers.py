from __future__ import absolute_import

from .fields import Field


class BaseSerializer(object):
    def __init__(self, data=None, source=None, required=True, many=False):
        self._initial_data = data
        self._source = source
        self._required = required
        self._many = many
        if self._many:
            self._validate_data = []
            self._errors = []
        else:
            self._validate_data = {}
            self._errors = {}

    def set_initial_data(self, data, index):
        self._initial_data = None
        if not data:
            return self

        if self._source in data:
            self._initial_data = data[self._source]
        elif index in data:
            self._initial_data = data[index]
        else:
            if self._required:
                self.add_error("initial_error", "This field is required")
        return self

    def validate_data(self):
        return self._validate_data

    def add_error(self, index, value):
        if self._many:
            self._errors.append({index: value})
        else:
            self._errors[index] = value

    def get_errors(self):
        return self._errors

    def has_error(self):
        return len(self._errors) != 0

    def is_valid(self):
        attributes = set(dir(self.__class__)) - set(dir(BaseSerializer))

        if not self._many:
            self._validate_data = self._validate(attributes, self._initial_data)
        else:
            if self._initial_data:
                assert isinstance(self._initial_data, list) or isinstance(self._initial_data, tuple), \
                    """ _initial_data must be list or tuple but get {data_type}""".format(
                        data_type=type(self._initial_data).__name__)
                for initial_data in self._initial_data:
                    validated_data = self._validate(attributes, initial_data)
                    if validated_data:
                        self._validate_data.append(validated_data)

        return not self.has_error()

    def _validate(self, attributes, initial_data):
        validate_data = {}
        for attr in attributes:
            field = getattr(self, attr)
            if isinstance(field, Field):
                field.set_data(initial_data, attr)
                if field.has_error():
                    self.add_error(attr, field.get_errors())
                    continue
                if not field.validate():
                    self.add_error(attr, field.get_errors())
                    continue
                validate_data[attr] = field.data
            elif isinstance(field, BaseSerializer):
                field.set_initial_data(initial_data, attr)
                if field.has_error():
                    self.add_error(attr, field.get_errors())
                    continue
                elif not field.is_valid():
                    self.add_error(attr, field.get_errors())
                validate_data[attr] = field.validate_data()
                continue
        return validate_data
