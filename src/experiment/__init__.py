from src.experiment.config import REDIS_CLIENT
from src.experiment.redis_connector import RedisConnector

redis_connector = RedisConnector.initialise(REDIS_CLIENT)
