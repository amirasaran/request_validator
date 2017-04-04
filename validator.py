class Validator(object):
    NOT_NULL = 'not_null'
    NOT_BLANK = 'not_blank'
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    REGEX = "regex"
    MAX_LEN = "max_len"
    MIN_LEN = "min_len"
    MAX_VALUE = "max_value"
    MIN_VALUE = "min_value"
    IN = "in"

    _MESSAGES = {
        NOT_NULL: "This field cannot be null",
        NOT_BLANK: "This field cannot be blank",
        INT: "This field must be integer",
        FLOAT: "This field must be float",
        STRING: "This field must be string but get {data_type}",
        MAX_LEN: "This field must be larger than {len} characters",
        MIN_LEN: "This field must be smaller than {len} characters",
        MAX_VALUE: "This field must be larger than {len}",
        MIN_VALUE: "This field must be smaller than {len}",
        IN: "This field must be choice from ({choices})",
        REGEX: "This field must be valid in pattern ({pattern})"
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
        self.error = self._MESSAGES[self.INT]
        return False

    def check_float(self):
        if isinstance(self.data, float):
            return True
        self.error = self._MESSAGES[self.INT]
        return False

    def check_string(self):
        if isinstance(self.data, str):
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
