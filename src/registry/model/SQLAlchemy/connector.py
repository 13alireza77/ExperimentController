from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class PostgresConnector():
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self):
        return self.Session()
