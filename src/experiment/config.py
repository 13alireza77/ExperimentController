import redis

REFRESH_EXPERIMENT_INTERVAL = 1 * 10

REDIS_CLIENT = redis.StrictRedis(host='localhost', port=6379)
