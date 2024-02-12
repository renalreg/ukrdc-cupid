import os
from dotenv import dotenv_values
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy_utils import database_exists, create_database
from ukrdc_sqla.ukrdc import Base as UKRDC3Base

# Load environment varibles from wither they are found
ENV = {**os.environ, **dotenv_values()}


class DatabaseConnection:
    def __init__(self, env_prefix: str = "UKRDC"):
        self.prefix = env_prefix

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

    def create_session(
        self, clean: bool = False, populate_tables: bool = False
    ) -> Session:
        # returns a squeaky clean (or otherwise if desired) session on db
        # defined by the environment variables.
        url = self.generate_database_url()
        if clean:
            if not database_exists(url):
                create_database(url)

        engine = create_engine(url=url)
        session = sessionmaker(bind=engine)()

        # just to be super sure we're not committing to something real
        db_real = self.name == "UKRDC3" or self.user != "postgres"

        if clean and self.name != "UKRDC3" or not db_real:
            # Create the database schema, tables, etc.
            UKRDC3Base.metadata.drop_all(bind=engine)
            UKRDC3Base.metadata.create_all(bind=engine)

            # initiate generation sequences for ids
            if self.prefix == "UKRDC" and clean:
                create_id_generation(session)
                print("pid generation")

            if populate_tables:
                # we need to populate the gp tables for cupid to work
                # auto_populate_gp()
                print(
                    "you need to import gp codes manually because of dependency conflicts"
                )
                print("this can be done by running g")
                # we should also copy codes from other lookup tables

        return session


def create_id_generation(ukrdc3: Session):

    sequence_sql = {
        "generate_new_pid": """
            CREATE SEQUENCE generate_new_pid
                START 1
                INCREMENT BY 1
                NO MAXVALUE
                NO CYCLE;

            SELECT setval('generate_new_pid', (SELECT COALESCE(MAX(pid)::integer, 0) + 1 FROM patientrecord));

            COMMENT ON SEQUENCE public.generate_new_pid
                IS 'Sequence to generate new pids should be initiated as the maxiumum pid';
            """,
        "generate_new_ukrdcid": """
            CREATE SEQUENCE generate_new_ukrdcid
                START 1
                INCREMENT BY 1
                NO MAXVALUE
                NO CYCLE;

            SELECT setval('generate_new_ukrdcid', (SELECT COALESCE(MAX(ukrdcid)::integer, 0) + 1 FROM patientrecord));

            COMMENT ON SEQUENCE public.generate_new_pid
                IS 'Sequence mints new ukrdcids';
            """,
    }

    sequencies = [
        seq[0] for seq in ukrdc3.execute("SELECT sequencename FROM pg_sequences;")
    ]

    for key, sql in sequence_sql.items():
        if key not in sequencies:
            ukrdc3.execute(text(sql))

    ukrdc3.commit()

    sequencies = ukrdc3.execute(text("SELECT * FROM pg_sequences;"))

    for ting in sequencies:
        print(ting)
