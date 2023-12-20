from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from ukrdc_sqla.ukrdc import Base as UKRDC3Base
import ukrdc_xsdata.ukrdc as xsd_ukrdc 

import pytest


def create_test_database(engine_url):
    if not database_exists(engine_url):
        create_database(engine_url)

# Update the connection string with your PostgreSQL details
connection_string = "postgresql://postgres:postgres@localhost/cupid_test_database"
create_test_database(connection_string)

engine = create_engine(connection_string)
ukrdc_sessionmaker = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Create the database schema, tables, etc.
UKRDC3Base.metadata.drop_all(bind=engine)
UKRDC3Base.metadata.create_all(bind=engine)

# Return the test session
ukrdc3_session = ukrdc_sessionmaker()