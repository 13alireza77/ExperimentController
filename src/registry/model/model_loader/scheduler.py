from registry.model.base import ModelRegistryInterface, ModelLoaderInterface, ExperimentModel


class ModelLoader(ModelLoaderInterface):
    def __init__(self, model_registry: ModelRegistryInterface, check_interval: int):
        super().__init__(model_registry, check_interval)

    def add_scheduler(self, model_name: str, experiment: str):
        """
        Starts a periodic task that checks for new model versions.
        """
        self.scheduler.add_job(
            self.monitor_new_model_version,
            'interval',
            seconds=self.check_interval,
            args=[model_name, experiment]
        )

    def start_scheduler(self):
        self.scheduler.start()

    def monitor_new_model_version(self, model_name: str, experiment: str):
        """
        Check the database for a newer version and load it if available.
        """
        latest_version = self.model_registry.get_last_version(model_name, experiment)
        experiment_model = ExperimentModel.get_instance()
        need_update_model = (experiment_model and experiment_model.version < latest_version) or (
                experiment_model is None)
        if need_update_model:
            ExperimentModel.set_instance(self.model_registry.load(model_name, experiment, latest_version))
