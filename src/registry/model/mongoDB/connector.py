from pymongo import MongoClient


class MongoDBConnector:
    def __init__(self, host: str, port: int, username: str = None, password: str = None,
                 db_name: str = "model_registry"):
        self.db_name = db_name
        self.client = MongoClient(host, port, username=username, password=password)
        self.db = self.client[self.db_name]

    def get_collection(self, collection_name):
        return self.db[collection_name]
