from pymongo import MongoClient


class MongoDBConnector:
    def __init__(self, host: str, port: int, username: str = None, password: str = None,
                 db_name: str = "experiment", collection_name: str = "model_registry"):
        self.client = MongoClient(host, port, username=username, password=password)
        self.collection = self.client[db_name][collection_name]
        self.collection.create_index([("name", 1), ("experiment", 1)])
        self.collection.create_index([("name", 1), ("experiment", 1), ("version", -1)], unique=True)
