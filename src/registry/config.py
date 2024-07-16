import redis

REDIS_CLIENT = redis.Redis()
REFRESH_EXPERIMENT_INTERVAL = 1 * 10
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %s - %(message)s'
