from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler


@dataclass
class ExperimentModel:
    model: object
    model_name: str
    version: int
    experiment: str
    _instance: 'ExperimentModel' = field(default=None, init=False, repr=False)

    def __new__(cls, *args, **kwargs):
        cls._instance = super().__new__(cls)

    @classmethod
    def get_instance(cls):
        return cls._instance

    @classmethod
    def set_instance(cls, instance):
        cls._instance = instance

    def __init__(self, model, model_name, version, experiment):
        if not hasattr(self, '_is_initialized'):
            super().__init__()
            self.model = model
            self.model_name = model_name
            self.version = version
            self.experiment = experiment
            self._is_initialized = True


class ModelRegistryInterface(ABC):
    @abstractmethod
    def register(self, model, model_name: str, experiment: str, version: Optional[int]):
        pass

    @abstractmethod
    def load(self, model_name: str, experiment: str, version: Optional[int]) -> BaseModel:
        pass

    def get_last_version(self, model_name: str, experiment: str):
        pass


class ModelLoaderInterface(ABC):

    def __init__(self, model_registry: ModelRegistryInterface, check_interval: int):
        self.model_registry = model_registry
        self.scheduler = BackgroundScheduler()
        self.check_interval = check_interval  # Check interval in seconds

    @abstractmethod
    def add_scheduler(self, model_name: str, experiment: str):
        pass

    def start_scheduler(self):
        pass

#
# class Registry:
#
#     def __init__(
#             self,
#             model_connector: ModelConnectorInterface,
#     ):
#         self._model_connector = model_connector
#
#     def register_model(self, model, model_name: str, experiment: str, version: Optional[int]):
#         self._model_connector.register(model, model_name, experiment, version)
#
#     def load_model(self, model, model_name: str, experiment: str, version: Optional[int]):
#         self._model_connector.load(model, model_name, experiment, version)
