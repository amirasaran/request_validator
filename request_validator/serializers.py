from __future__ import absolute_import

import copy

from .fields import Field


class BaseSerializer(object):
    def __init__(self, data=None, source=None, required=True, force_valid=False):
        self._initial_data = data
        self._source = source
        self._required = required
        self._force_valid = force_valid
        self._errors = None
        self._validated_data = None

    def get_errors(self):
        return self._errors

    def validate_data(self):
        return self._validated_data

    def has_error(self):
        return len(self._errors) != 0

    @property
    def errors(self):
        return self.get_errors()


class Serializer(BaseSerializer):
    def __init__(self, *args, **kwargs):
        super(Serializer, self).__init__(*args, **kwargs)
        self._validated_data = {}
        self._errors = {}
        self._default = {}
        self._all_fields_valid = True

    def validate_data(self):
        if not (self._force_valid and self.has_error()) and self._all_fields_valid:
            return self._validated_data
        return {}

    def __new__(cls, *args, **kwargs):
        many = kwargs.pop("many", False)
        cls.fields()
        if many:
            return ListSerializer(cls, *args, **kwargs)
        else:
            return object.__new__(cls, *args, **kwargs)

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
        self._errors[index] = value

    def is_valid(self):
        validated_data, serializer_validated = self._validate(self._initial_data)
        self._validated_data = validated_data
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
            elif isinstance(field,  Serializer):
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
            elif isinstance(field, ListSerializer):
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
    def is_all_fields_valid(self):
        return self._all_fields_valid

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
                self.add_error(index, "This field is required")
        return self


class ListSerializer(BaseSerializer):
    def __init__(self, serializer, *args, **kwargs):
        super(ListSerializer, self).__init__(*args, **kwargs)
        self._serializer = serializer
        self._validated_data = []
        self._errors = []
        self._args = args
        self._kwargs = kwargs
        self._data = []
        self._default = []

    def add_error(self, value):
        self._errors.append(value)

    def is_valid(self):
        assert isinstance(self._initial_data, list) or isinstance(self._initial_data, tuple), \
            """ _initial_data must be list or tuple but get {data_type}""".format(
                data_type=type(self._initial_data).__name__)

        for initial_data in self._initial_data:
            serializer = self._serializer(data=initial_data, *self._args, **self._kwargs)
            if serializer.is_valid():
                self._validated_data.append(serializer.validate_data())
                self._data.append(serializer.data)
            else:
                self.add_error(serializer.get_errors())
                if not self._force_valid and serializer.validate_data():
                    self._validated_data.append(serializer.validate_data())
                    self._data.append(serializer.data)

        return not self.has_error()

    @property
    def data(self):
        return self._data

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
                self.add_error("This field is required")
        return self


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