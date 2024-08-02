from typing import Optional

from mlflow.entities.model_registry import ModelVersion

from registry.exception import ModelNotFound
from registry.model.base import ModelRegistryInterface, ExperimentModel
from registry.model.mlflow.connector import Connector


class MlFlowModelRegistry(ModelRegistryInterface):
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

    def load(self, model_name: str, experiment: str, version: Optional[int]) -> ExperimentModel:
        """
        Load the model using model_name and experiment_manager. Version is optional, if not provided, latest is assumed.
        """
        if version is None:
            versions = self.client.search_model_versions(f"name='{model_name}'")
            if versions:
                latest_version_info = max(versions, key=lambda x: int(x.version))
                version = latest_version_info.version
            else:
                raise ModelNotFound(
                    f"No model found for {model_name} under experiment {experiment} with version {version}")

        model_uri = f"models:/{model_name}/{version}"
        return ExperimentModel(
            model=self.client.pyfunc.load_model(model_uri=model_uri),
            model_name=model_name,
            version=version,
            experiment=experiment
        )

    def get_last_version(self, model_name: str, experiment: str):
        versions = self.client.search_model_versions(f"name='{model_name}'")
        if versions:
            latest_version_info = max(versions, key=lambda x: int(x.version))
            return latest_version_info.version
        else:
            raise ModelNotFound(
                f"No model found for {model_name} under experiment {experiment}")
