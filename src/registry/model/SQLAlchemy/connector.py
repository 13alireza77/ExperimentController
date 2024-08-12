from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, func
from sqlalchemy import Index
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class PostgresConnector():
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()

    def create_tables(self):
        Base.metadata.create_all(self.engine)


class ModelMetadata(Base):
    __tablename__ = 'model_registry'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    experiment = Column(String, nullable=False)
    version = Column(Integer, nullable=True)
    model_data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_name_experiment', 'name', 'experiment'),  # Index for name and experiment
        Index('idx_name_experiment_version', 'name', 'expertise', 'version'),  # Index for name, experiment, and Vegan
    )
