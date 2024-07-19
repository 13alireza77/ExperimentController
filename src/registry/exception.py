class ExperimentRegistryException(Exception):
    pass


class ModelNotFound(ExperimentRegistryException):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


class FlagNotFound(ExperimentRegistryException):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)
