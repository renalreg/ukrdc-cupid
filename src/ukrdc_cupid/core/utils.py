import os
from dotenv import dotenv_values
from urllib.parse import urlparse

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy_utils import (
    database_exists,
    create_database,
)  # type:ignore
from ukrdc_sqla.ukrdc import Base as UKRDC3Base

from ukrdc_cupid.core.investigate.models import Base as InvestiBase
from ukrdc_cupid.core.investigate.utils import update_issue_types
from ukrdc_cupid.core.store.models.lookup_tables import GPInfoType

# Load environment varibles from wither they are found
ENV = {**os.environ, **dotenv_values(".env"), **dotenv_values(".env.test")}

# There is probably a better home for these than this.
ID_SEQUENCES = {
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


class DatabaseConnection:
    def __init__(self, env_prefix: str = "UKRDC", url=None):
        self.prefix = env_prefix
        self.url = url

        self.driver = self.get_property("driver", "scheme")
        self.user = self.get_property("user", "username")
        self.password = self.get_property("password", "password")
        self.port = self.get_property("port", "port")
        self.name = self.get_property("name", "path").strip("/")

        if not self.url:
            self.url = self.generate_database_url()

        self.engine = create_engine(url=self.url)
        # self.engine = create_engine(url=self.url)

    def get_property(self, property_name: str, url_property: str) -> str:
        if self.url:
            parsed_url = urlparse(self.url)
            return getattr(parsed_url, url_property, "")
        else:
            return self.get_env_value(property_name)

    def get_env_value(self, field_name: str) -> str:
        env_key = f"{self.prefix}_{field_name}".upper()
        env_value = ENV.get(env_key)

        if env_value:
            return env_value
        else:
            return

    def generate_database_url(self) -> str:
        return f"{self.driver}://{self.user}:{self.password}@localhost:{self.port}/{self.name}"

    def create_sessionmaker(self) -> sessionmaker:

        db_sessionmaker = sessionmaker(bind=self.engine)

        return db_sessionmaker


def create_id_generation_sequences(session: Session):
    # run sequences for generating PID and UKRDCID if they don't exist
    db_sequencies = session.execute(text("SELECT sequencename FROM pg_sequences;"))
    sequencies = [seq[0] for seq in db_sequencies]

    for key, sql in ID_SEQUENCES.items():
        if key not in sequencies:
            session.execute(text(sql))


def populate_ukrdc_tables(session: Session, gp_info: bool = False):
    """Function populates various tables to allow foreign key relationships

    Args:
        session (Session): _description_
    """
    # populate gp_info this is optional as can be slow
    if gp_info:
        GPInfoType(session).update_gp_info_table()

    # we should have something for tables imported from ukrr

    # populate issue types table
    update_issue_types(session)


class UKRDCConnection(DatabaseConnection):
    def __init__(self, url=None):
        super().__init__("UKRDC", url)

    def generate_schema(self):
        """Creates db if it doesn't exist and generates the schema for it."""
        if not database_exists(self.url):
            create_database(self.url)

        if self.prefix == "UKRDC":
            # generate main ukrdc tables
            UKRDC3Base.metadata.drop_all(bind=self.engine)
            UKRDC3Base.metadata.create_all(bind=self.engine)

            # generate schema and tables for investigations
            schema_name = "investigations"
            with self.engine.connect() as connection:
                trans = connection.begin()
                connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
                trans.commit()

            InvestiBase.metadata.drop_all(bind=self.engine)
            InvestiBase.metadata.create_all(bind=self.engine)
        else:
            raise Exception("Sorry bro only implemented for ukrdc")


class UKRRConnection(DatabaseConnection):
    def __init__(
        self,
    ):
        ukrr_url = ENV["UKRR_URL"]
        super().__init__(url=ukrr_url)
