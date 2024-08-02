import dataclasses
import json
from typing import Optional

import redis

from src.experiment.base import Experiment, Flag


class RedisConnector:
    _redis_client: redis.Redis
    _prefix_flag_experiments_key = "flag_experiments"
    _prefix_flag_key = "flag"

    @classmethod
    def initialise(cls, redis_client: redis.Redis):
        cls._redis_client = redis_client
        return cls

    @staticmethod
    def _get_flag_experiments_key(flag_name: str):
        return f"{RedisConnector._prefix_flag_experiments_key}_{flag_name}"

    @staticmethod
    def _get_flag_key(flag_name: str):
        return f"{RedisConnector._prefix_flag_key}_{flag_name}"

    @classmethod
    def save_experiment(cls, experiment: Experiment, ttl: Optional[int] = None):
        key = cls._get_flag_experiments_key(experiment.flag_name)
        cls._redis_client.hset(key, experiment.name, json.dumps(dataclasses.asdict(experiment)))
        if ttl:
            cls._redis_client.expire(key, ttl)

    @classmethod
    def save_flag(cls, flag: Flag, ttl: Optional[int] = None):
        key = cls._get_flag_key(flag.name)
        cls._redis_client.set(key, json.dumps(dataclasses.asdict(flag)))
        if ttl is not None:
            cls._redis_client.expire(key, ttl)

    @classmethod
    def load_experiments_by_flag_name(cls, flag_name: str):
        key = cls._get_flag_experiments_key(flag_name)
        return cls._redis_client.hvals(key)

    @classmethod
    def load_flag(cls, flag_name: str):
        key = cls._get_flag_key(flag_name)
        return cls._redis_client.get(key)

    @classmethod
    def delete_experiments_by_flag_name(cls, flag_name: str):
        cls._redis_client.delete(cls._get_flag_experiments_key(flag_name))

    @classmethod
    def delete_experiment(cls, flag_name: str, experiment_name: str):
        cls._redis_client.hdel(cls._get_flag_experiments_key(flag_name), experiment_name)
