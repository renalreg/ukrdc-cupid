from dotenv import dotenv_values
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

ENV = dotenv_values()

class DatabaseConnection():
    def __init__(self, prefix:str = "UKRDC"):
        self.prefix = prefix

    @property
    def driver(self) -> str:
        return self.get_env_value("DRIVER")

    @property
    def user(self) -> str:
        return self.get_env_value("USER")

    @property
    def password(self) -> str:
        return self.get_env_value("PASS")

    @property
    def port(self) -> int:
        return int(self.get_env_value("PORT"))

    @property
    def name(self) -> str:
        return self.get_env_value("NAME")
    
    def get_env_value(self, field_name: str) -> str:
        env_key = f"{self.prefix}_{field_name}".upper()
        env_value = ENV.get(env_key)
        if env_value is None:
            raise ValueError(f"Environment variable {env_key} not found.")
        return env_value

    def generate_database_url(self) -> str:
        return f"{self.driver}://{self.user}:{self.password}@localhost:{self.port}/{self.name}"

    def create_session(self) -> Session:
        engine = create_engine(self.generate_database_url())
        Session = sessionmaker(bind=engine)
        return Session()