import pickle
from datetime import datetime
from typing import Optional, List

from experiment.base import AiModel
from src.registry.exception import ModelNotFound
from src.registry.model.SQLAlchemy.connector import PostgresConnector, ModelMetadata
from src.registry.model.base import ModelRegistryInterface, ExperimentModel


class PostgresModelRegistry(ModelRegistryInterface):
    def __init__(self, postgres_connector: PostgresConnector):
        self.session = postgres_connector.get_session()
        postgres_connector.create_tables()  # Ensure tables are created

    def _get_latest_version(self, model_name, experiment):
        return self.session.query(ModelMetadata).filter_by(name=model_name, experiment=experiment).order_by(
            ModelMetadata.version.desc()).first()

    def register(self, model, model_name: str, experiment: str, version: Optional[int]):
        """
        Register a new model or create a new version in PostgreSQL.
        """
        if version is None:
            try:
                version = self.get_last_version(model_name=model_name, experiment=experiment)
            except ModelNotFound:
                version = 0
        model_data = pickle.dumps(model)
        new_model = ModelMetadata(
            name=model_name,
            experiment=experiment,
            version=version,
            model_data=model_data,
            created_at=datetime.utcnow(),
        )
        self.session.add(new_model)
        self.session.commit()

    def load(self, model_name: str, experiment: str, version: Optional[int]) -> ExperimentModel:
        """
        Load the model using model_name, experiment, and version. If the version is None, the latest is assumed.
        """
        model = self._get_latest_version(model_name, experiment) if version is None else self.session.query(
            ModelMetadata).filter_by(name=model_name, experiment=experiment, version=version).one_or_none()

        if model is None:
            raise ModelNotFound(
                f"No model found for {model_name} under experiment {experiment} with version {version}")
        return ExperimentModel(
            model=pickle.loads(model.model_data),
            model_name=model_name,
            version=version,
            experiment=experiment,
            created_at=model.created_at,
        )

    def get_last_version(self, model_name: str, experiment: str):
        """
        Retrieve the latest version number of a model given its name and experiment.
        """
        latest_version = self._get_latest_version(model_name, experiment)
        if latest_version is None:
            raise ModelNotFound(f"No versions found for model {model_name} under experiment {experiment}")

        return latest_version.version

    def get_all_experiments_versions(self, experiments: List[str]):
        """
        Retrieve all the versions of a model given a list of experiment names.
        """
        query = (ModelMetadata.name, ModelMetadata.version, ModelMetadata.experiment)

        versions = self.session.query(*query).filter(ModelMetadata.experiment.in_(experiments)) \
            .order_by(ModelMetadata.version).all()
        if not versions:
            raise ModelNotFound(f"No versions found under experiments {', '.join(experiments)}")

        return [AiModel(name=name, experiment_name=experiment, version=version)
                for name, version, experiment in versions]
