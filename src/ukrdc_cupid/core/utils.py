import os
from dotenv import dotenv_values
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy_utils import (
    database_exists,
    create_database,
    drop_database,
)  # type:ignore
from ukrdc_sqla.ukrdc import Base as UKRDC3Base

from ukrdc_cupid.core.investigate.models import Base as InvestiBase
from ukrdc_cupid.core.investigate.utils import update_issue_types
from ukrdc_cupid.core.store.models.lookup_tables import GPInfoType

# Load environment varibles from wither they are found
ENV = {**os.environ, **dotenv_values()}


class DatabaseConnection:
    def __init__(self, env_prefix: str = "UKRDC", url=None):
        self.prefix = env_prefix
        if not url:
            self.url = self.generate_database_url()
        else:
            self.url = url

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
    ) -> sessionmaker:
        # returns a squeaky clean (or otherwise if desired) session on db
        # defined by the environment variables. This might need to be thought
        # out more carefully when used on a live system.

        if clean:
            if not database_exists(self.url):
                create_database(self.url)

        engine = create_engine(url=self.url)
        db_sessionmaker = sessionmaker(bind=engine)

        with db_sessionmaker() as session:
            # just to be super sure we're not committing to something real
            db_real = self.name == "UKRDC3" or self.user != "postgres"

            if clean:
                # build a clean ukrdc
                if self.prefix == "UKRDC" and not db_real:
                    # Create the database schema, tables, etc.
                    UKRDC3Base.metadata.drop_all(bind=engine)
                    UKRDC3Base.metadata.create_all(bind=engine)

                    # initiate generation sequences for ids
                    create_id_generation(session)

                if self.prefix == "INVESTIGATE":
                    InvestiBase.metadata.drop_all(bind=engine)
                    InvestiBase.metadata.create_all(bind=engine)

                if populate_tables and self.prefix == "UKRDC":
                    # we need to populate the gp tables for cupid to work
                    # auto_populate_gp()
                    GPInfoType(session).update_gp_info_table()

                if populate_tables and self.prefix == "INVESTIGATE":
                    update_issue_types(session)

        return db_sessionmaker

    def teardown_db(self):
        if database_exists(self.url):
            drop_database(self.url)


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
