from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from apscheduler.schedulers.background import BackgroundScheduler

from src.experiment.base import AiModel


@dataclass
class ExperimentModel:
    model: object
    model_name: str
    version: int
    experiment: str
    updated_at: datetime


@dataclass
class ExperimentModelSingleton:
    experiment_model: ExperimentModel = None
    _instance: 'ExperimentModelSingleton' = field(default=None, init=False, repr=False)

    def __new__(cls, *args, **kwargs):
        cls._instance = super().__new__(cls)

    @classmethod
    def get_instance(cls):
        return cls._instance

    @classmethod
    def set_instance(cls, instance):
        cls._instance = instance

    def __init__(self, experiment_model: ExperimentModel):
        if not hasattr(self, '_is_initialized'):
            super().__init__()
            self._is_initialized = True
            self.experiment_model = experiment_model


class ModelRegistryInterface(ABC):
    STARTING_VERSION = 1

    @abstractmethod
    def register(self, model, model_name: str, flag: str, experiments: List[str], version: Optional[int] = None):
        pass

    @abstractmethod
    def update(self, model_name: str, flag: str, experiments: List[str], version: int) -> None:
        pass

    @abstractmethod
    def load(self, experiment: str, model_name: Optional[str] = None, version: Optional[int] = None) -> ExperimentModel:
        pass

    @abstractmethod
    def get_last_version_by_flag(self, model_name: str, experiment: str):
        pass

    @abstractmethod
    def get_all_flag_models(self, flag: str) -> List[AiModel]:
        pass


class ModelLoaderInterface(ABC):

    def __init__(self, model_registry: ModelRegistryInterface, check_interval: int):
        self.model_registry = model_registry
        self.scheduler = BackgroundScheduler()
        self.check_interval = check_interval  # Check interval in seconds

    @abstractmethod
    def add_scheduler(self, model_name: str, flag: str, experiment: str):
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
