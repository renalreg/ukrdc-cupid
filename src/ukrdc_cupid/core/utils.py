import os
from dotenv import dotenv_values
from urllib.parse import urlparse

from sqlalchemy.pool import QueuePool
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy_utils import (
    database_exists,
    create_database,
)  # type:ignore
from ukrdc_sqla.ukrdc import Base as UKRDC3Base

from ukrdc_cupid.core.investigate.models import Base as InvestiBase
from ukrdc_cupid.core.investigate.utils import update_picklists
from ukrdc_cupid.core.store.models.lookup_tables import GPInfoType

# Load environment varibles from wither they are found

ENV = {
    **os.environ,  # The docker stack loads directly into env
    **dotenv_values(".env"),  # Otherwise we use an env file
    **dotenv_values(".env.test"),
    **dotenv_values(".env.docker"),
}

# There is probably a better home for these than this.
ID_SEQUENCES = {
    "generate_new_pid": """
        CREATE SEQUENCE generate_new_pid
            START 1
            INCREMENT BY 1
            NO MAXVALUE
            NO CYCLE;

        SELECT setval('generate_new_pid', (SELECT COALESCE(MAX(pid)::integer, 0) + 1 FROM patientrecord));

        COMMENT ON SEQUENCE generate_new_pid
            IS 'Sequence to generate new pids should be initiated as the maxiumum pid';
        """,
    "generate_new_ukrdcid": """
        CREATE SEQUENCE generate_new_ukrdcid
            START 1
            INCREMENT BY 1
            NO MAXVALUE
            NO CYCLE;

        SELECT setval('generate_new_ukrdcid', (SELECT COALESCE(MAX(ukrdcid)::integer, 0) + 1 FROM patientrecord));

        COMMENT ON SEQUENCE generate_new_ukrdcid
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
        self.name = self.get_property("name", "path")
        self.host = self.get_property("host", "hostname")

        if self.host == "":
            self.host = "localhost"

        self.engine = None

        if self.name is not None:
            self.name = self.name.strip("/")

        if (
            self.url is None
            and self.driver is not None
            and self.user is not None
            and self.password is not None
            and self.port is not None
            and self.name is not None
        ):
            self.url = self.generate_database_url()

        if self.url is not None:
            self.engine = self.get_engine()

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
        return f"{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    def get_engine(self) -> Engine:
        return create_engine(url=self.url)

    def create_sessionmaker(self) -> sessionmaker:

        db_sessionmaker = sessionmaker(bind=self.engine)

        return db_sessionmaker


class UKRDCConnection(DatabaseConnection):
    def __init__(self, url=None):
        self.pool_size = ENV.get("UKRDC_POOL_SIZE", 10)
        super().__init__("UKRDC", url)

    def get_engine(self) -> Engine:
        # We want to limit the number of connections to the database at any one
        # time. In theory mirth shouldn't spin up lots of connections but we
        # want to be sure.
        return create_engine(
            url=self.url,
            poolclass=QueuePool,
            pool_size=self.pool_size,
            max_overflow=10,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True,
        )


class UKRRConnection(DatabaseConnection):
    def __init__(
        self,
    ):
        ukrr_url = ENV.get("UKRR_URL")
        if ukrr_url is not None:
            super().__init__(url=ukrr_url)
        else:
            raise Exception("UKRR URL not found")


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

    # TODO: populate lookup tables

    # populate issue types table
    update_picklists(session)


def generate_schema(
    user: str, schema_name: str, sqla_base: declarative_base, engine: Engine
):
    """Generate schema for database."""

    # This little bit of sql isn't essential but it helps with replicating
    # the structure of the ukrdc
    schema_generation_sql = f"""
    CREATE SCHEMA IF NOT EXISTS
        {schema_name}
        AUTHORIZATION {user};

    GRANT ALL ON SCHEMA {schema_name} TO {user};
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA {schema_name} TO {user};
    """

    with engine.connect() as connection:
        trans = connection.begin()
        connection.execute(text(schema_generation_sql))
        connection.execute(text(f"SET search_path TO {schema_name}"))
        trans.commit()

    # Generate main ukrdc tables
    sqla_base.metadata.drop_all(bind=engine)
    sqla_base.metadata.create_all(bind=engine)

    return


def generate_database(url: str, gp_info=False):
    """Creates db if it doesn't exist and generates the schema for it.
    This probably shouldn't be used in production.

    Args:
        url: Database URL
        gp_info: Whether to populate GP info table (can be slow)
    """

    # create database (useful for testing)
    if not database_exists(url):
        create_database(url)

    # Connect and generate tables and schema
    conn = UKRDCConnection(url=url)
    generate_schema(conn.user, "extract", UKRDC3Base, conn.engine)
    generate_schema(conn.user, "investigations", InvestiBase, conn.engine)

    # install postgres module(s) and change default search path
    with conn.engine.connect() as connection:
        trans = connection.begin()
        connection.execute(
            text(
                f'ALTER DATABASE {conn.name} SET search_path TO "$user", extract, investigations;'
            )
        )
        connection.execute(text("CREATE EXTENSION pg_trgm;"))
        connection.execute(text("CREATE EXTENSION fuzzystrmatch;"))
        trans.commit()

    # Close and recreate the engine to get a fresh connection with the new search path
    conn.engine.dispose()
    conn = UKRDCConnection(url=url)
    ukrdc_sessionmaker = conn.create_sessionmaker()

    # Add generation sequences for pid and ukrdcid
    with ukrdc_sessionmaker() as session:
        create_id_generation_sequences(session)
        populate_ukrdc_tables(session, gp_info=gp_info)
        session.commit()

    return ":)"
