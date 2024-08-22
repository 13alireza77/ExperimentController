from abc import ABC, abstractmethod
from typing import Optional


class DataRegisteryInterface(ABC):
    @abstractmethod
    def publish(self, data, data_name: str, experiment: str, version: Optional[int] = None, **kwargs):
        pass

    @abstractmethod
    def load(self, data_name: str, experiment: str, version: Optional[int] = None, **kwargs):
        pass
