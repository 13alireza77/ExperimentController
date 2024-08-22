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
    experiment: Optional[str]
    flag: str
    updated_at: datetime


@dataclass
class ExperimentModelSingleton:
    experiment_model: ExperimentModel = None
    _instances: dict = field(default_factory=dict, init=False, repr=False)

    def __new__(cls, experiment_model: ExperimentModel):
        key = experiment_model.experiment or experiment_model.flag
        if experiment_model.experiment not in cls._instances:
            instance = super().__new__(cls)
            instance.experiment_model = experiment_model
            instance._is_initialized = False
            cls._instances[key] = instance
        return cls._instances[key]

    def __init__(self, experiment_model: ExperimentModel):
        if not self._is_initialized:
            self.experiment_model = experiment_model
            self._is_initialized = True

    @classmethod
    def get_instance(cls, experiment: str) -> ExperimentModel:
        cls._ensure_instances_initialized()
        experiment_model_singleton = cls._instances.get(experiment, None)
        if experiment_model_singleton:
            return experiment_model_singleton.experiment_model

    @classmethod
    def _ensure_instances_initialized(cls):
        if '_instances' not in cls.__dict__:
            cls._instances = {}

    @classmethod
    def clear_instances(cls):
        cls._instances.clear()


class ModelRegistryInterface(ABC):
    STARTING_VERSION = 1

    @abstractmethod
    def register(self, model, model_name: str, flag: str, experiments: List[str], version: Optional[int] = None) -> int:
        pass

    @abstractmethod
    def update(self, model_name: str, flag: str, experiments: List[str], version: int) -> None:
        pass

    @abstractmethod
    def load(self, flag: str, experiment: str = None, model_name: Optional[str] = None,
             version: Optional[int] = None) -> ExperimentModel:
        pass

    @abstractmethod
    def get_last_version(self, flag: str, model_name: str = None, experiment: Optional[str] = None) -> int:
        pass

    @abstractmethod
    def get_all_flag_models_specifications(self, flag: str) -> List[AiModel]:
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
