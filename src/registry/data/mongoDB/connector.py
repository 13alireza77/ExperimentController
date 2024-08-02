import json
from typing import Optional

from bson.json_util import dumps
from pymongo import MongoClient

from registry.data.base import DataConnectorInterface


class MongoDBDataConnector(DataConnectorInterface):
    def __init__(self, uri: str, database_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[database_name]

    @staticmethod
    def _format_document_name(data_name, experiment, version):
        return f"{data_name}_{experiment}_{version}"

    def publish(self, data, data_name: str, experiment: str, version: Optional[int]):
        collection_name = self._format_document_name(data_name, experiment, version)
        collection = self.db[collection_name]
        if isinstance(data, dict):
            collection.insert_one(data)
        elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
            collection.insert_many(data)
        else:
            raise ValueError("Data must be a dictionary or a list of dictionaries")

    def load(self, data_name: str, experiment: str, version: Optional[int]):
        collection_name = self._format_document_name(data_name, experiment, version)
        collection = self.db[collection_name]
        return json.loads(dumps(collection.find({})))
