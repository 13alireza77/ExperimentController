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

    def register(self, model, model_name: str, flag: str, experiments: List[str], version: Optional[int] = None) -> int:
        """
        Register a new model or create a new version in PostgreSQL.
        """
        current_time = datetime.utcnow()
        model_data = pickle.dumps(model)
        new_model = ModelMetadata(
            name=model_name,
            flag=flag,
            experiments=experiments,
            model_data=model_data,
            updated_at=current_time,
        )

        if version is None:
            try:
                last_version = self.get_last_version(flag=flag) + 1
                new_model.version = last_version
            except ModelNotFound:
                new_model.version = self.STARTING_VERSION
                new_model.created_at = current_time
        else:
            new_model.version = version

        self.session.add(new_model)
        self.session.commit()

        return new_model.version

    def load(self, flag: str, experiment: str = None, model_name: Optional[str] = None,
             version: Optional[int] = None) -> ExperimentModel:
        """
        Load the model using model_name, experiment, and version. If the version is None, the latest is assumed.
        """
        query = self.session.query(ModelMetadata).filter(ModelMetadata.flag == flag)

        if experiment:
            query = query.filter(ModelMetadata.experiments.contains([experiment]))

        if version is None:
            query = query.order_by(ModelMetadata.version.desc())
        else:
            query = query.filter(ModelMetadata.version == version)

        if model_name:
            query = query.filter(ModelMetadata.name == model_name)

        model = query.first()

        if model is None:
            raise ModelNotFound(
                f"No model found for {model_name} under experiment {experiment} with version {version}")
        return ExperimentModel(
            model=pickle.loads(model.model_data),
            model_name=model.name,
            version=model.version,
            experiment=experiment,
            updated_at=model.updated_at,
            flag=model.flag,
        )

    def update(self, model_name: str, flag: str, experiments: List[str], version: int) -> None:
        model_record = self.session.query(ModelMetadata).filter(
            ModelMetadata.name == model_name,
            ModelMetadata.flag == flag,
            ModelMetadata.version == version
        ).first()

        if not model_record:
            raise ModelNotFound(f"Model {model_name} with flag {flag} and version {version} not found.")

        # Extend the current experiments list with new experiments avoiding duplicates
        if model_record.experiments is not None:
            updated_experiments = list(set(model_record.experiments + experiments))
        else:
            updated_experiments = experiments

        # Update the experiments field and modified timestamp
        model_record.experiments = updated_experiments
        model_record.updated_at = datetime.utcnow()

        # Commit transaction
        self.session.commit()

    def get_last_version(self, flag: str, model_name: str = None, experiment: Optional[str] = None) -> int:
        """
        Retrieve the latest version number of a model given its name and experiment.
        """

        query = self.session.query(ModelMetadata.version).filter(ModelMetadata.flag == flag)

        if model_name:
            query = query.filter(ModelMetadata.name == model_name)

        if experiment:
            query = query.filter(ModelMetadata.experiments.contains([experiment]))

        latest_version = query.order_by(ModelMetadata.version.desc()).one_or_none()

        if not latest_version:
            raise ModelNotFound(f"No versions found for model {model_name} under flag {flag}")
        return latest_version

    def get_all_flag_models_specifications(self, flag: str) -> List[AiModel]:
        """
        Retrieve all the versions of a model given a list of experiment names.
        """
        query = (ModelMetadata.name, ModelMetadata.version)

        models = self.session.query(*query).filter(ModelMetadata.flag.is_(flag)) \
            .order_by(ModelMetadata.version).all()
        if not models:
            raise ModelNotFound(f"No versions found under flag {flag}")

        return [AiModel(name=name, version=version) for name, version in models]
