from abc import ABC, abstractmethod
from typing import Optional


class ModelConnectorInterface(ABC):
    @abstractmethod
    def register(self, model, model_name: str, experiment: str, version: Optional[int]):
        pass

    @abstractmethod
    def load(self, model_name: str, experiment: str, version: Optional[int]):
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
