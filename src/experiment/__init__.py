from src.experiment.experiment_manager import ExperimentManager
from src.registry.model.mongoDB.connector import MongoDBConnector
from src.registry.model.mongoDB.model import MongoDBModelRegistry
from src.experiment.config import REDIS_CLIENT
from src.experiment.redis_connector import RedisConnector

redis_connector = RedisConnector.initialise(REDIS_CLIENT)
reg = MongoDBModelRegistry(MongoDBConnector('localhost', 27017, 'mongoadmin', 'secret'))
ExperimentManager.initialise(reg, redis_connector)
