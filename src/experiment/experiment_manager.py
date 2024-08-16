import json
from typing import Optional, Union, List

import cachetools.func

from src.experiment.base import Experiment, Flag, ExperimentFlagType, AiModel
from src.experiment.config import REFRESH_EXPERIMENT_INTERVAL
from src.experiment.exception import ExperimentNotFound, FlagNotFound
from src.experiment.redis_connector import RedisConnector
from src.registry.exception import ModelNotFound
from src.registry.model.base import ModelRegistryInterface, ExperimentModel


class ExperimentManager:
    _redis_connector: RedisConnector
    _experiments_with_cumulative_share = {}
    _model_registry: ModelRegistryInterface

    @classmethod
    def initialise(cls, model_registry: ModelRegistryInterface, redis_connector: RedisConnector):
        cls._model_registry = model_registry
        cls._redis_connector = redis_connector

    @classmethod
    def save_experiment(cls, experiment: Experiment):
        cls._redis_connector.save_experiment(experiment)
        if experiment.ai_model:
            cls._model_registry.update(model_name=experiment.ai_model.name, flag=experiment.flag_name,
                                       version=experiment.ai_model.version, experiments=[experiment.name])

    @classmethod
    def delete_experiment(cls, flag_name: str, experiment_name: str):
        cls._redis_connector.delete_experiment(flag_name, experiment_name)

    @classmethod
    def save_flag(cls, flag: Flag):
        cls._redis_connector.save_flag(flag)

    @classmethod
    def delete_flag(cls, flag_name: str):
        cls._redis_connector.delete_flag(flag_name)

    @classmethod
    @cachetools.func.ttl_cache(maxsize=10, ttl=REFRESH_EXPERIMENT_INTERVAL)
    def _get_flag(cls, flag_name: str) -> Optional[Flag]:
        data = cls._redis_connector.get_flag(flag_name)
        if data:
            return cls._deserialize_flag(data)
        return None

    @classmethod
    def evaluate(cls, flag_name: str, layer: str, layer_value: Optional[Union[str, int]]):
        cls.get_experiments_by_flag_name(flag_name=flag_name)
        if not cls._experiments_with_cumulative_share:
            raise ExperimentNotFound(f"Experiments with flag name:{flag_name} not found")
        experiment_range = cls._experiment_to_range(flag_name, layer, layer_value)
        for cumulative_share, experiment in cls._experiments_with_cumulative_share.items():
            if experiment_range <= cumulative_share:
                return experiment.flag_value

        flag = cls._get_flag(flag_name)
        if not flag:
            raise FlagNotFound(f"Flag with name:{flag_name} not found")
        return flag.base_value

    @classmethod
    def get_flag_ai_models(cls, flag: str) -> List[AiModel]:
        try:
            return cls._model_registry.get_all_flag_models(flag)
        except ModelNotFound:
            return []

    @classmethod
    def get_experiment_ai_model(cls, experiment: str) -> Optional[ExperimentModel]:
        try:
            return cls._model_registry.load(experiment)
        except ModelNotFound:
            return None

    @classmethod
    @cachetools.func.ttl_cache(maxsize=10, ttl=REFRESH_EXPERIMENT_INTERVAL)
    def get_experiments_by_flag_name(cls, flag_name: str):
        all_data = cls._redis_connector.get_experiments_by_flag_name(flag_name)
        deserialize_experiments = [cls._deserialize_experiment(data) for data in all_data]
        cumulative_share = 0
        for deserialize_experiment in deserialize_experiments:
            cumulative_share += deserialize_experiment.share
            cls._experiments_with_cumulative_share[cumulative_share] = deserialize_experiment
        return deserialize_experiments

    @classmethod
    def get_experiment_by_flag_name(cls, flag_name: str, experiment_name: str):
        experiment = cls._redis_connector.get_experiment_by_flag_name(flag_name, experiment_name)
        return cls._deserialize_experiment(experiment)

    @classmethod
    def _deserialize_experiment(cls, item: str) -> Experiment:
        data = json.loads(item)
        experiment = Experiment(
            name=data['name'],
            flag_name=data['flag_name'],
            flag_value=data['flag_value'],
            share=data['share'],
            layer=data['layer'],
            ai_model=None

        )
        if data.get('ai_model'):
            experiment.ai_model = AiModel.from_dict(data['ai_model'])
        return experiment

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
