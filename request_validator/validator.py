from __builtin__ import unicode


class Validator(object):
    NOT_NULL = 'not_null'
    NOT_BLANK = 'not_blank'
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    REGEX = "regex"
    DATE = "date"
    DATETIME = "datetime"
    MAX_LEN = "max_len"
    MIN_LEN = "min_len"
    MAX_VALUE = "max_value"
    MIN_VALUE = "min_value"
    IN = "in"

    _MESSAGES = {
        NOT_NULL: "This field cannot be null",
        NOT_BLANK: "This field cannot be blank",
        INT: "This field must be integer but get {data_type}",
        FLOAT: "This field must be float  {data_type}",
        STRING: "This field must be string but get {data_type}",
        MAX_LEN: "This field must be larger than {len} characters",
        MIN_LEN: "This field must be smaller than {len} characters",
        MAX_VALUE: "This field must be larger than {len}",
        MIN_VALUE: "This field must be smaller than {len}",
        IN: "This field must be choice from ({choices})",
        REGEX: "This field must be valid in pattern ({pattern})",
        DATE: "This field must be valid date (format='{date_format}') but given data is {data}",
        DATETIME: "This field must be valid datetime (format='{date_format}') but given data is {data}"
    }

    def __init__(self, data, validator, value=None):
        self.data = data
        self._validator = "check_{}".format(validator)
        self._value = value
        self.error = ""

    def get_message(self):
        return self.error

    def validate(self):
        return getattr(self, self._validator)()

    def check_not_null(self):
        if self.data is not None:
            return True
        self.error = self._MESSAGES[self.NOT_NULL]
        return False

    def check_not_blank(self):
        if self.data != "":
            return True
        self.error = self._MESSAGES[self.NOT_BLANK]
        return False

    def check_int(self):
        if isinstance(self.data, int):
            return True
        if isinstance(self.data, (str, unicode)):
            import re
            if re.match(r"\d+", self.data):
                self.data = int(self.data)
                return True

        self.error = self._MESSAGES[self.INT].format(data_type=type(self.data).__name__)
        return False

    def check_float(self):
        if isinstance(self.data, float):
            return True
        if isinstance(self.data, int):
            self.data = float(self.data)
            return True
        self.error = self._MESSAGES[self.FLOAT].format(data_type=type(self.data).__name__)
        return False

    def check_string(self):
        if isinstance(self.data, (str, unicode)):
            return True
        self.error = self._MESSAGES[self.STRING].format(data_type=type(self.data).__name__)
        return False

    def check_max_len(self):
        if len(self.data) <= self._value:
            return True
        self.error = self._MESSAGES[self.MAX_LEN].format(len=self._value)
        return False

    def check_min_len(self):
        if len(self.data) >= self._value:
            return True
        self.error = self._MESSAGES[self.MIN_LEN].format(len=self._value)
        return False

    def check_max_value(self):
        if self.data <= self._value:
            return True
        self.error = self._MESSAGES[self.MAX_VALUE].format(len=self._value)
        return False

    def check_min_value(self):
        if self.data >= self._value:
            return True
        self.error = self._MESSAGES[self.MIN_VALUE].format(len=self._value)
        return False

    def check_in(self):
        if self.data in self._value:
            return True
        self.error = self._MESSAGES[self.IN].format(choices=",".join(self._value))
        return False

    def check_regex(self):
        import re
        if re.match(self._value, self.data):
            return True
        self.error = self._MESSAGES[self.REGEX].format(pattern=self._value)
        return False

    def check_date(self):
        if isinstance(self.data, (str, unicode)):
            self.data = self.data.strip()
        import datetime
        if self._value['convert_to_date']:
            if isinstance(self.data, datetime.datetime):
                self.data = self.data.date()
                return True
            elif isinstance(self.data, datetime.date):
                return True
            elif isinstance(self.data, str):
                try:
                    self.data = datetime.datetime.strptime(self.data, self._value['format']).date()
                    return True
                except Exception as e:
                    self.error = self._MESSAGES[self.DATE].format(date_format=self._value['format'],
                                                                  data=self.data)
                    return False
        else:
            if isinstance(self.data, datetime.datetime):
                self.data = self.data.date().strftime(self._value['format'])
                return True
            elif isinstance(self.data, datetime.date):
                self.data = self.data.strftime(self._value['format'])
                return True
            elif isinstance(self.data, str):
                try:
                    self.data = datetime.datetime.strptime(
                        self.data,
                        self._value['format']
                    ).date().strftime(self._value['format'])
                    return True
                except Exception as e:
                    self.error = self._MESSAGES[self.DATE].format(date_format=self._value['format'],
                                                                  data=self.data)
                    return False
        self.error = self._MESSAGES[self.DATE].format(date_format=self._value['format'], data=self.data)
        return False

    def check_datetime(self):
        if isinstance(self.data, (str, unicode)):
            self.data = self.data.strip()

        import datetime
        if self._value['convert_to_datetime']:
            if isinstance(self.data, datetime.datetime):
                return True
            elif isinstance(self.data, datetime.date):
                self.data = datetime.datetime(self.data.year, self.data.month, self.data.day)
                return True
            elif isinstance(self.data, (str, unicode)):
                try:
                    self.data = datetime.datetime.strptime(self.data, self._value['format'])
                    return True
                except Exception as e:
                    self.error = self._MESSAGES[self.DATETIME].format(date_format=self._value['format'], data=self.data)
                    return False
        else:
            if isinstance(self.data, datetime.datetime):
                self.data = self.data.strftime(self._value['format'])
                return True
            elif isinstance(self.data, datetime.date):
                self.data = datetime.datetime(self.data.year, self.data.month, self.data.day).strftime(
                    self._value['format'])
                return True
            elif isinstance(self.data, (str, unicode)):
                self.data = datetime.datetime.strptime(
                    self.data,
                    self._value['format']
                ).strftime(self._value['format'])
                try:
                    self.data = datetime.datetime.strptime(
                        self.data,
                        self._value['format']
                    ).strftime(self._value['format'])
                    return True
                except Exception as e:
                    self.error = self._MESSAGES[self.DATETIME].format(date_format=self._value['format'], data=self.data)
                    return False
        self.error = self._MESSAGES[self.DATETIME].format(date_format=self._value['format'], data=self.data)
        return False
