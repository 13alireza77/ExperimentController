import os

import mlflow
from mlflow.tracking import MlflowClient


class Connector:
    def __init__(self, uri, username, password, experiment_name):
        self._uri = uri
        self._username = username
        self._password = password
        self.experiment_name = experiment_name
        self.client = None
        # Handling authentication and connecting:
        self._set_authentication()

    def _set_authentication(self):
        """
        Set basic authentication for accessing the MLFlow server.
        This is hypothetical and assumes you have a way to leverage these environment variables.
        """
        os.environ['MLFLOW_TRACKING_USERNAME'] = self._username
        os.environ['MLFLOW_TRACKING_PASSWORD'] = self._password

    def initialise(self):
        mlflow.set_tracking_uri(self._uri)
        if not mlflow.get_experiment_by_name(self.experiment_name):
            mlflow.create_experiment(self.experiment_name)
        mlflow.set_experiment(self.experiment_name)
        self.client = MlflowClient()
