import json
from typing import Optional, Union

import cachetools.func

from src.experiment import redis_connector
from src.experiment.base import Experiment, Flag, ExperimentFlagType
from src.experiment.config import REFRESH_EXPERIMENT_INTERVAL
from src.experiment.exception import ExperimentNotFound, FlagNotFound
from src.experiment.redis_connector import RedisConnector


class ExperimentManager:
    _redis_connector: RedisConnector = redis_connector
    _experiments_with_cumulative_share = {}

    @classmethod
    def save_experiment(cls, experiment: Experiment):
        cls._redis_connector.save_experiment(experiment)

    @classmethod
    def save_flag(cls, flag: Flag):
        cls._redis_connector.save_flag(flag)

    @classmethod
    @cachetools.func.ttl_cache(maxsize=10, ttl=REFRESH_EXPERIMENT_INTERVAL)
    def _load_flag(cls, flag_name: str) -> Optional[Flag]:
        data = cls._redis_connector.load_flag(flag_name)
        if data:
            return cls._deserialize_flag(data)
        return None

    @classmethod
    def evaluate(cls, flag_name: str, layer: str, layer_value: Optional[Union[str, int]]):
        cls._load_experiments_by_flag_name(flag_name=flag_name)
        if not cls._experiments_with_cumulative_share:
            raise ExperimentNotFound(f"Experiments with flag name:{flag_name} not found")
        experiment_range = cls._experiment_to_range(flag_name, layer, layer_value)
        for cumulative_share, experiment in cls._experiments_with_cumulative_share.items():
            if experiment_range <= cumulative_share:
                return experiment.flag_value

        flag = cls._load_flag(flag_name)
        if not flag:
            raise FlagNotFound(f"Flag with name:{flag_name} not found")
        return flag.base_value

    @classmethod
    @cachetools.func.ttl_cache(maxsize=10, ttl=REFRESH_EXPERIMENT_INTERVAL)
    def _load_experiments_by_flag_name(cls, flag_name: str) -> dict:
        all_data = cls._redis_connector.load_experiments_by_flag_name(flag_name)
        cumulative_share = 0
        for data in all_data:
            deserialize_experiment = cls._deserialize_experiment(data)
            cumulative_share += deserialize_experiment.share
            cls._experiments_with_cumulative_share[cumulative_share] = deserialize_experiment

    @classmethod
    def _deserialize_experiment(cls, item: str) -> Experiment:
        data = json.loads(item)
        return Experiment(
            name=data['name'],
            flag_name=data['flag_name'],
            flag_value=data['flag_value'],
            share=data['share'],
            layer=data['layer'],
        )

    @classmethod
    def _experiment_to_range(cls, flag_name, layer, layer_value):
        flag_name_str = str(flag_name)
        layer_str = str(layer)
        layer_value_str = str(layer_value)

        composite_key = f"{flag_name_str}|{layer_str}|{layer_value_str}"

        hash_value = hash(composite_key)

        mapped_value = abs(hash_value) % 101

        return mapped_value / 100

    @classmethod
    def _deserialize_flag(cls, item: str) -> Flag:
        data = json.loads(item)
        return Flag(name=data['name'],
                    type=ExperimentFlagType[data['type']],
                    base_value=data['base_value'])
