from pymongo import MongoClient


class MongoDBConnector:
    def __init__(self, host: str, port: int, username: str = None, password: str = None,
                 db_name: str = "experiment", collection_name: str = "model_registry"):
        self.client = MongoClient(host, port, username=username, password=password)
        self.database = self.client[db_name]
        self.collection = self.client[db_name][collection_name]
        self.collection.create_index([("name", 1), ("experiments", 1)])
        self.collection.create_index([("flag", 1), ("name", 1), ("experiments", 1), ("version", -1)], unique=True)
