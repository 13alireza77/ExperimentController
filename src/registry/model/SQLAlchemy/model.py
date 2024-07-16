import pickle
from typing import Optional

from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base

from registry.SQLAlchemy.connector import PostgresConnector
from src.registry.base import ModelConnectorInterface

Base = declarative_base()


class ModelMetadata(Base):
    __tablename__ = 'models'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    experiment = Column(String, nullable=False)
    version = Column(Integer, nullable=True)
    model_data = Column(LargeBinary, nullable=False)


class PostgresModelRegistry(ModelConnectorInterface):
    def __init__(self, postgres_connector: PostgresConnector):
        self.session = postgres_connector.get_session()

    def _get_latest_version(self, model_name, experiment):
        return self.session.query(ModelMetadata).filter_by(name=model_name, experiment=experiment).order_by(
            ModelMetadata.version.desc()).first()

    def register(self, model, model_name: str, experiment: str, version: Optional[int]):
        """
        Register a new model or create a new version in PostgreSQL.
        """
        model_data = pickle.dumps(model)
        new_model = ModelMetadata(
            name=model_id,
            experiment=experiment,
            version=version,
            model_data=model_data
        )
        self.session.add(new_model)
        self.session.commit()

    def load(self, model_name: str, experiment: str, version: Optional[int]):
        """
        Load the model using model_name, experiment, and version. If the version is None, the latest is assumed.
        """
        model = self._get_latest_version(model_name, experiment) if version is None else self.session.query(
            ModelMetadata).filter_by(name=model_name, experiment=experiment, version=version).one_or_none()

        if model is None:
            raise ValueError(f"No model found for {model_name} under experiment {experiment} with version {version}.")

        return pickle.loads(model.model_data)
