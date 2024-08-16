from registry.model.base import ModelRegistryInterface, ModelLoaderInterface, ExperimentModelSingleton
from src.experiment import ExperimentManager


class ModelLoader(ModelLoaderInterface):
    def __init__(self, model_registry: ModelRegistryInterface, check_interval: int):
        super().__init__(model_registry, check_interval)

    def add_scheduler(self, model_name: str, flag: str, experiment: str):
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

    def get_last_version(self, model_name: str, flag: str, experiment: str):
        experiment = ExperimentManager.get_experiment_by_flag_name(flag_name=flag, experiment_name=experiment)
        if experiment and experiment.ai_model:
            return experiment.ai_model.version
        else:
            ai_model = self.model_registry.load(model_name=model_name, experiment=experiment)
            if experiment and ai_model:
                experiment.ai_model = ai_model
                ExperimentManager.save_experiment(experiment)
            return ai_model.version

    def _monitor_new_model_version(self, model_name: str, flag: str, experiment: str):
        """
        Check the database for a newer version and load it if available.
        """
        latest_version = self.get_last_version(model_name, flag, experiment)
        experiment_model = ExperimentModelSingleton.get_instance()
        need_update_model = (experiment_model and experiment_model.version < latest_version) or (
                experiment_model is None)
        if need_update_model:
            ExperimentModelSingleton.set_instance(
                self.model_registry.load(model_name=model_name, experiment=experiment, version=latest_version))
