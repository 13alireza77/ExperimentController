from typing import Optional

from mlflow.entities.model_registry import ModelVersion

from registry.model.base import ModelConnectorInterface
from registry.model.mlflow.connector import Connector


class MlFlowModelRegistry(ModelConnectorInterface):
    def __init__(self, mlflow_connector: Connector):
        if not isinstance(mlflow_connector, Connector):
            raise ValueError("mlflow_connector should be an instance of MlFlowConnector")
        self.client = mlflow_connector.client

    @staticmethod
    def _get_tags(experiment: str, version: Optional[int]):
        return {"experiment_manager": experiment, "version": version}

    def register(self, model, model_name: str, experiment: str, version: Optional[int]) -> ModelVersion:
        """
        Notice: must log model before calling this method
        Register a new model or create new version in the MLFlow.
        """
        run_id = self.client.active_run().info.run_id
        model_uri = f"runs:/{run_id}/{model_name}"
        self.client.create_registered_model(
            name=model_name,
            tags=self._get_tags(experiment, version)
        )
        return self.client.create_model_version(name=model_name, source=model_uri, run_id=run_id)

    def load(self, model_name: str, experiment: str, version: Optional[int]):
        """
        Load the model using model_name and experiment_manager. Version is optional, if not provided, latest is assumed.
        """
        if version is None:
            versions = self.client.search_model_versions(f"name='{model_name}'")
            if versions:
                latest_version_info = max(versions, key=lambda x: int(x.version))
                version = latest_version_info.version
            else:
                raise ValueError(f"No versions found for model '{model_name}'.")

        model_uri = f"models:/{model_name}/{version}"
        return self.client.pyfunc.load_model(model_uri=model_uri)
