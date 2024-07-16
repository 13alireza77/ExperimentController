import pickle
from typing import Optional

import gridfs

from registry.model.base import ModelConnectorInterface
from registry.model.mongoDB.connector import MongoDBConnector


class MongoDBModelRegistry(ModelConnectorInterface):
    def __init__(self, mongo_connector: MongoDBConnector):
        self.db = mongo_connector.db
        self.fs = gridfs.GridFS(self.db)

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
        self.db.models.insert_one(new_model)

    def load(self, model_name: str, experiment: str, version: Optional[int]):
        """
        Load the model using model_name, experiment, and version. If version is None, latest is assumed.
        """
        query = {"name": model_name, "experiment": experiment}
        if version is not None:
            query["version"] = version
        model_document = self.db.models.find_one(query, sort=[("version", -1)])

        if not model_document:
            raise ValueError(f"No model found for {model_name} in experiment {experiment} with version {version}.")

        model_file = self.fs.get(model_document["model_file_id"])
        model = pickle.loads(model_file.read())
        return model
