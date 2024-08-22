from src.experiment.base import AiModel
from registry.model.base import ModelRegistryInterface, ModelLoaderInterface, ExperimentModelSingleton
from src.experiment.experiment_manager import ExperimentManager


class ModelLoader(ModelLoaderInterface):
    def __init__(self, model_registry: ModelRegistryInterface, check_interval: int):
        super().__init__(model_registry, check_interval)

    def add_scheduler(self, model_name: str, flag: str, experiment: str = None):
        """
        Starts a periodic task that checks for new model versions.
        """
        self.scheduler.add_job(
            self._monitor_new_model_version,
            'interval',
            seconds=self.check_interval,
            args=[model_name, flag, experiment]
        )

    def start_scheduler(self):
        self.scheduler.start()

    def get_last_version(self, model_name: str, flag_name: str, experiment_name: str = None):
        experiment = None
        if experiment_name:
            experiment = ExperimentManager.get_experiment_by_flag_name(flag_name=flag_name,
                                                                       experiment_name=experiment_name)
            if experiment and experiment.ai_model:
                return experiment.ai_model.version

        flag = ExperimentManager.get_flag(flag_name=flag_name)
        if flag and flag.ai_model:
            return flag.ai_model.version

        last_version = self.model_registry.get_last_version(flag=flag_name, model_name=model_name)
        if experiment and last_version:
            experiment.ai_model = AiModel(name=model_name, version=last_version)
            ExperimentManager.save_experiment(experiment)
        elif flag and last_version:
            flag.ai_model = AiModel(name=model_name, version=last_version)
            ExperimentManager.save_flag(flag)

        return last_version

    def _monitor_new_model_version(self, model_name: str, flag: str, experiment: str = None):
        """
        Check the database for a newer version and load it if available.
        """
        latest_version = self.get_last_version(model_name, flag, experiment)
        experiment_model = ExperimentModelSingleton.get_instance(experiment)
        need_update_model = (experiment_model and experiment_model.version != latest_version) or (
                experiment_model is None)
        if need_update_model:
            ExperimentModelSingleton(
                self.model_registry.load(flag=flag, model_name=model_name, experiment=experiment,
                                         version=latest_version))
