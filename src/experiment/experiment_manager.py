import json
from typing import Optional, Union, List

import cachetools.func

from src.experiment.base import Experiment, Flag, ExperimentFlagType, AiModel
from src.experiment.config import REFRESH_EXPERIMENT_INTERVAL
from src.experiment.exception import ExperimentNotFound, FlagNotFound
from src.experiment.redis_connector import RedisConnector
from src.registry.data.base import DataRegisteryInterface
from src.registry.exception import ModelNotFound
from src.registry.model.base import ModelRegistryInterface, ExperimentModel


class ExperimentManager:
    _redis_connector: RedisConnector
    _experiments_with_cumulative_share = {}
    _model_registry: ModelRegistryInterface
    _data_registry: DataRegisteryInterface

    @classmethod
    def initialise(cls, model_registry: ModelRegistryInterface, redis_connector: RedisConnector,
                   data_registry: DataRegisteryInterface):
        cls._model_registry = model_registry
        cls._redis_connector = redis_connector
        cls._data_registry = data_registry

    @classmethod
    def save_experiment(cls, experiment: Experiment, need_update_model_registry: bool = True):
        cls._redis_connector.save_experiment(experiment)
        if experiment.ai_model and need_update_model_registry:
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
    def evaluate(cls, flag_name: str, layer: str, layer_value: Optional[Union[str, int]]):
        cls.get_experiments_by_flag_name(flag_name=flag_name)
        if not cls._experiments_with_cumulative_share:
            raise ExperimentNotFound(f"Experiments with flag name:{flag_name} not found")
        experiment_range = cls._experiment_to_range(flag_name, layer, layer_value)
        for cumulative_share, experiment in cls._experiments_with_cumulative_share.items():
            if experiment_range <= cumulative_share:
                return experiment.flag_value, experiment.name

        flag = cls.get_flag(flag_name)
        if not flag:
            raise FlagNotFound(f"Flag with name:{flag_name} not found")
        return flag.base_value, None

    @classmethod
    def get_flag_ai_models_specifications(cls, flag_name: str) -> List[AiModel]:
        try:
            return cls._model_registry.get_all_flag_models_specifications(flag_name)
        except ModelNotFound:
            return []

    @classmethod
    def get_ai_model(cls, flag_name: str, experiment_name: str = None, model_name: str = None,
                     model_version: int = None) -> Optional[ExperimentModel]:
        flag = cls.get_flag(flag_name)
        if not flag:
            raise FlagNotFound(f"Flag with name:{flag_name} not found")

        if experiment_name:
            experiment = cls.get_experiment_by_flag_name(flag_name=flag_name, experiment_name=experiment_name)

            if experiment is None:
                raise ExperimentNotFound(f"Experiment {experiment_name} not found")

            if experiment.ai_model:
                if model_name is None:
                    model_name = experiment.ai_model.name
                if model_version is None:
                    model_version = experiment.ai_model.version

        if flag.ai_model:
            if model_name is None:
                model_name = flag.ai_model.name
            if model_version is None:
                model_version = flag.ai_model.version

        try:
            return cls._model_registry.load(flag=flag_name,
                                            experiment=experiment_name,
                                            model_name=model_name,
                                            version=model_version)
        except ModelNotFound:
            return None

    @classmethod
    @cachetools.func.ttl_cache(maxsize=10, ttl=REFRESH_EXPERIMENT_INTERVAL)
    def get_experiments_by_flag_name(cls, flag_name: str) -> List[Experiment]:
        all_data = cls._redis_connector.get_experiments_by_flag_name(flag_name)
        deserialize_experiments = [cls._deserialize_experiment(data) for data in all_data]
        deserialize_experiments.sort(key=lambda x: x.flag_value)
        cumulative_share = 0
        for deserialize_experiment in deserialize_experiments:
            cumulative_share += deserialize_experiment.share
            cls._experiments_with_cumulative_share[cumulative_share] = deserialize_experiment
        return deserialize_experiments

    @classmethod
    def get_experiment_by_flag_name(cls, flag_name: str, experiment_name: str) -> Optional[Experiment]:
        experiment = cls._redis_connector.get_experiment_by_flag_name(flag_name, experiment_name)
        if experiment:
            return cls._deserialize_experiment(experiment)

    @classmethod
    def register_ai_model(cls, model, model_name: str, flag_name: str, experiment_name: str,
                          version: Optional[int] = None):
        experiment = cls.get_experiment_by_flag_name(flag_name=flag_name, experiment_name=experiment_name)

        if experiment is None:
            raise ExperimentNotFound(f"Experiment {experiment_name} not found")

        registered_model_version = cls._model_registry.register(model=model,
                                                                model_name=model_name,
                                                                flag=flag_name,
                                                                experiments=[experiment_name],
                                                                version=version)
        experiment.ai_model = AiModel(name=model_name, version=registered_model_version)
        cls.save_experiment(experiment, need_update_model_registry=False)

    @classmethod
    def load_ai_model_data(cls, data_name: str, flag_name: str, experiment_name: str, **kwargs):

        experiment = cls.get_experiment_by_flag_name(flag_name=flag_name, experiment_name=experiment_name)

        if experiment is None:
            raise ExperimentNotFound(f"Experiment {experiment_name} not found")

        return cls._data_registry.load(data_name=data_name, experiment=experiment_name, **kwargs)

    @classmethod
    def publish_ai_model_data(cls, data, data_name: str, flag_name: str, experiment_name: str,
                              version: Optional[int] = None, **kwargs):

        experiment = cls.get_experiment_by_flag_name(flag_name=flag_name, experiment_name=experiment_name)

        if experiment is None:
            raise ExperimentNotFound(f"Experiment {experiment_name} not found")

        return cls._data_registry.publish(data=data, data_name=data_name, experiment=experiment_name, **kwargs)

    @classmethod
    def get_flag(cls, flag_name: str) -> Optional[Flag]:
        data = cls._redis_connector.get_flag(flag_name)
        if data:
            return cls._deserialize_flag(data)
        return None

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
        flag = Flag(name=data['name'],
                    type=ExperimentFlagType[data['type']],
                    base_value=data['base_value'],
                    ai_model=None)
        if data.get('ai_model'):
            flag.ai_model = AiModel.from_dict(data['ai_model'])
        return flag
