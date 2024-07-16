from abc import ABC, abstractmethod
from typing import Optional


class DataConnectorInterface(ABC):
    @abstractmethod
    def publish(self, data, data_name: str, experiment: str, version: Optional[int]):
        pass

    @abstractmethod
    def load(self, data_name: str, experiment: str, version: Optional[int]):
        pass
