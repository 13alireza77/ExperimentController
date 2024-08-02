import pickle
from typing import Optional

import gridfs

from registry.exception import ModelNotFound
from registry.model.base import ModelRegistryInterface, ExperimentModel
from registry.model.mongoDB.connector import MongoDBConnector


class MongoDBModelRegistry(ModelRegistryInterface):
    def __init__(self, mongo_connector: MongoDBConnector):
        self.collection = mongo_connector.collection
        self.fs = gridfs.GridFS(mongo_connector.database, self.collection.name)

    def register(self, model, model_name: str, experiment: str, version: Optional[int]):
        """
        Register a new model or create a new version in MongoDB.
        """
        model_data = pickle.dumps(model)
        file_id = self.fs.put(model_data)
        new_model = {
            "name": model_name,
            "experiment": experiment,
            "version": version,
            "model_file_id": file_id
        }
        self.collection.insert_one(new_model)

    def load(self, model_name: str, experiment: str, version: Optional[int]) -> ExperimentModel:
        """
        Load the model using model_name, experiment, and version. If version is None, latest is assumed.
        """
        query = {"name": model_name, "experiment": experiment}
        if version is not None:
            query["version"] = version
        model_document = self.collection.find_one(query, sort=[("version", -1)])

        if not model_document:
            raise ModelNotFound(f"No model found for {model_name} under experiment {experiment} with version {version}")

        model_file = self.fs.get(model_document["model_file_id"])
        model = pickle.loads(model_file.read())
        return ExperimentModel(
            model=model,
            model_name=model_name,
            version=version,
            experiment=experiment
        )

    def get_last_version(self, model_name: str, experiment: str):
        """
        Retrieve the latest version number of a model given its name and experiment.
        """
        latest_version_document = self.collection.find_one(
            {"name": model_name, "experiment": experiment},
            sort=[("version", -1)])

        if not latest_version_document:
            raise ModelNotFound(f"No versions found for model {model_name} under experiment {experiment}")

        return latest_version_document['version']
