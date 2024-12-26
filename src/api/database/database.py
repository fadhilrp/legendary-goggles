from sqlmodel import Session, create_engine, SQLModel


class Database:
    def __init__(self, sqlite_url: str = "sqlite:///database.db"):
        connect_args = {"check_same_thread": False}
        self.engine = create_engine(sqlite_url, connect_args=connect_args)

    def create_tables(self):
        SQLModel.metadata.create_all(self.engine)

    def get_session(self):
        return Session(self.engine)