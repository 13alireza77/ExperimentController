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

        # Configure RDB to snapshot less frequently
        # Save every 5 minutes if at least 1 keys change
        cls._redis_client.config_set('save', '300 1')

        # Enable AOF with everysec fsync policy
        cls._redis_client.config_set('appendonly', 'yes')
        cls._redis_client.config_set('appendfsync', 'everysec')

        # Configure background AOF rewrite settings
        cls._redis_client.config_set('auto-aof-rewrite-percentage', '100')
        cls._redis_client.config_set('auto-aof-rewrite-min-size', '64mb')

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
        experiment_data = dataclasses.asdict(experiment)
        if experiment.ai_model:
            experiment_data['ai_model'] = experiment.ai_model.to_dict()
        else:
            experiment_data['ai_model'] = None
        cls._redis_client.hset(key, experiment.name, json.dumps(experiment_data))
        if ttl:
            cls._redis_client.expire(key, ttl)

    @classmethod
    def save_flag(cls, flag: Flag, ttl: Optional[int] = None):
        key = cls._get_flag_key(flag.name)
        flag_data = dataclasses.asdict(flag)
        if flag.ai_model:
            flag_data['ai_model'] = flag.ai_model.to_dict()
        else:
            flag_data['ai_model'] = None
        cls._redis_client.set(key, json.dumps(flag_data))
        if ttl is not None:
            cls._redis_client.expire(key, ttl)

    @classmethod
    def get_experiments_by_flag_name(cls, flag_name: str):
        key = cls._get_flag_experiments_key(flag_name)
        return cls._redis_client.hvals(key)

    @classmethod
    def get_experiment_by_flag_name(cls, flag_name: str, experiment_name: str):
        return cls._redis_client.hget(cls._get_flag_experiments_key(flag_name), experiment_name)

    @classmethod
    def get_flag(cls, flag_name: str):
        key = cls._get_flag_key(flag_name)
        return cls._redis_client.get(key)

    @classmethod
    def delete_experiments_by_flag_name(cls, flag_name: str):
        cls._redis_client.delete(cls._get_flag_experiments_key(flag_name))

    @classmethod
    def delete_experiment(cls, flag_name: str, experiment_name: str):
        cls._redis_client.hdel(cls._get_flag_experiments_key(flag_name), experiment_name)

    @classmethod
    def delete_flag(cls, flag_name: str):
        cls._redis_client.delete(cls._get_flag_key(flag_name))
