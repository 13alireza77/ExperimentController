class ExperimentManagerException(Exception):
    pass


class ExperimentNotFound(ExperimentManagerException):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


class FlagNotFound(ExperimentManagerException):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


class ModelDataNotFound(ExperimentManagerException):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)
