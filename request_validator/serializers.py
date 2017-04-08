from __future__ import absolute_import

import copy

from .fields import Field


class BaseSerializer(object):
    def __init__(self, data=None, source=None, required=True, many=False, force_valid=False):
        self._initial_data = data
        self._source = source
        self._required = required
        self._many = many
        self._force_valid = force_valid
        self._all_fields_valid = True
        if self._many:
            self._validate_data = []
            self._errors = []
            self._default = []
        else:
            self._validate_data = {}
            self._errors = {}
            self._default = {}

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

    def __new__(cls, *args, **kwargs):
        cls.fields()
        return object.__new__(cls, *args, **kwargs)

    def validate_data(self):
        if self._many:
            if not (self._force_valid and not self.has_error()):
                return self._validate_data
            return []
        else:
            if not (self._force_valid and self.has_error()) and self._all_fields_valid:
                return self._validate_data
            return {}

    @classmethod
    def fields(cls):
        if not hasattr(cls, "_fields_dict"):
            fields = {}
            for field in cls._get_fields():
                fields[field] = getattr(cls, field)
                delattr(cls, field)
            setattr(cls, '_fields_dict', fields)
        return getattr(cls, '_fields_dict')

    @classmethod
    def _get_fields(cls):
        if not hasattr(cls, '_fields'):
            cls._fields = []
            for field in set(dir(cls)) - set(dir(BaseSerializer)):
                if not isinstance(getattr(cls, field), (Field, BaseSerializer)):
                    continue
                cls._fields.append(field)
        return cls._fields

    def _get_field(self, key):
        return copy.deepcopy(getattr(self, '_fields_dict')[key])

    @property
    def data(self):
        data = self.validate_data()
        for key, value in self.fields().items():
            if key not in data:
                data[key] = value._default
        return data

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
        if not self._many:
            validated_data, serializer_validated = self._validate(self._initial_data)
            # if not (self._force_valid and serializer_validated):
            self._validate_data = validated_data
        else:
            if self._initial_data:
                assert isinstance(self._initial_data, list) or isinstance(self._initial_data, tuple), \
                    """ _initial_data must be list or tuple but get {data_type}""".format(
                        data_type=type(self._initial_data).__name__)
                for initial_data in self._initial_data:
                    validated_data, serializer_validated = self._validate(initial_data)
                    if validated_data:
                        if not (self._force_valid and not serializer_validated):
                            self._validate_data.append(validated_data)

        return not self.has_error()

    def _validate(self, initial_data):
        serializer_validated = True
        validate_data = {}
        errors, initial_data = self._check_user_validation(initial_data)

        if len(errors) != 0:
            self._all_fields_valid = False
            for error in errors:
                for key, value in error.iteritems():
                    self.add_error(key, value)

        for attr in self.fields():
            field = self._get_field(attr)
            if isinstance(field, Field):
                field.set_data(initial_data, attr)
                if field.has_error():
                    self._all_fields_valid = False
                    serializer_validated = False
                    self.add_error(attr, field.get_errors())
                    continue
                if not field.validate():
                    serializer_validated = False
                    self.add_error(attr, field.get_errors())
                    continue
                validate_data[attr] = field.data
            elif isinstance(field, BaseSerializer):
                field.set_initial_data(initial_data, attr)
                if field.has_error():
                    self._all_fields_valid = False
                    serializer_validated = False
                    self.add_error(attr, field.get_errors())
                    continue
                elif not field.is_valid():
                    serializer_validated = False
                    self.add_error(attr, field.get_errors())
                validate_data[attr] = field.validate_data()
                continue
        return validate_data, serializer_validated

    def _check_user_validation(self, data):
        try:
            before_validation = self.validate(data)
            return [], before_validation
        except ValidationError as e:
            return e.details, data

    def validate(self, attr):
        return attr

    @property
    def all_fields_valid(self):
        return self._all_fields_valid

    @property
    def errors(self):
        return self.get_errors()


class ValidationError(Exception):
    def __init__(self, details):

        self.details = []
        if not isinstance(details, list):
            details = [details]
        for detail in details:
            if not isinstance(detail, dict):
                self.details.append({'non_field_error': str(detail)})
            else:
                self.details.append(detail)
