class ExperimentManager(Exception):
    pass


class ExperimentNotFound(ExperimentManager):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)


class FlagNotFound(ExperimentManager):
    def __init__(self, message=None):
        self.message = message
        super().__init__(message)
