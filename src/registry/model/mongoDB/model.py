import pickle
from datetime import datetime
from typing import Optional, List

import gridfs

from src.experiment.base import AiModel
from src.registry.exception import ModelNotFound
from src.registry.model.base import ModelRegistryInterface, ExperimentModel
from src.registry.model.mongoDB.connector import MongoDBConnector


class MongoDBModelRegistry(ModelRegistryInterface):
    def __init__(self, mongo_connector: MongoDBConnector):
        self.collection = mongo_connector.collection
        self.fs = gridfs.GridFS(mongo_connector.database, self.collection.name)

    def register(self, model, model_name: str, flag: str, experiments: List[str], version: Optional[int] = None):
        """
        Register a new model or create a new version in MongoDB.
        """
        current_time = datetime.utcnow()

        model_data = pickle.dumps(model)
        file_id = self.fs.put(model_data)

        new_model = {
            "name": model_name,
            "flag": flag,
            "experiments": experiments,
            "model_file_id": file_id,
            "updated_at": current_time,
        }

        if version is None:
            try:
                new_model['version'] = self.get_last_version_by_flag(model_name=model_name, flag=flag)['version']
            except ModelNotFound:
                new_model['version'] = self.STARTING_VERSION
                new_model['created_at'] = current_time
        else:
            new_model['version'] = version

        self.collection.insert_one(new_model)

    def update(self, model_name: str, flag: str, experiments: List[str], version: int) -> None:
        """
        Register a new model or create a new version in MongoDB.
        """
        self.collection.find_one_and_update(
            filter={"flag": flag, "name": model_name, "version": version},
            update={
                "$set": {"updated_at": datetime.utcnow()},
                "$addToSet": {"experiments": {"$each": experiments}}
            }, return_document=False)

    def load(self, experiment: str, model_name: Optional[str] = None, version: Optional[int] = None) -> ExperimentModel:
        """
        Load the model using model_name, experiment, and version. If version is None, latest is assumed.
        """
        query = {"experiments": {"$in": [experiment]}}
        if version:
            query["version"] = version
        if model_name:
            query["name"] = model_name

        model_document = self.collection.find_one(query, sort=[("version", -1)])

        if not model_document:
            raise ModelNotFound(f"No model found for {model_name} under experiment {experiment} with version {version}")

        model_file = self.fs.get(model_document["model_file_id"])
        model = pickle.loads(model_file.read())
        return ExperimentModel(
            model=model,
            model_name=model_document['name'],
            version=model_document['version'],
            experiment=experiment,
            updated_at=model_document['updated_at']
        )

    def get_last_version_by_flag(self, model_name: str, flag: str) -> dict:
        """
        Retrieve the latest version number of a model given its name and experiment.
        """
        latest_version_document = self.collection.find_one(
            {"flag": flag, "name": model_name},
            sort=[("version", -1)])

        if not latest_version_document:
            raise ModelNotFound(f"No versions found for model {model_name} under flag {flag}")

        return latest_version_document

    def get_all_flag_models(self, flag: str) -> List[AiModel]:
        """
        Retrieve all the versions of a model given its names and a list of experiments, optionally including the creation date.
        """
        documents = list(
            self.collection.find({"flag": flag}, {"name": 1, "version": 1}).sort(
                "version", 1))

        if not documents:
            raise ModelNotFound(f"No versions found under flag {flag}")

        return [AiModel(name=doc["name"], version=doc["version"]) for doc in documents]
