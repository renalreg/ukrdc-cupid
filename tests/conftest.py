import uuid
import pytest

from ukrdc_cupid.core.utils import (
    UKRDCConnection,
    create_id_generation_sequences,
    populate_ukrdc_tables,
)
from ukrdc_cupid.api import app
from ukrdc_cupid.api.main import get_session

from sqlalchemy_utils import (
    database_exists,
    drop_database,
)  # type:ignore

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def ukrdc_sessionmaker(url: str, gp_info: bool = False):
    """_summary_

    Args:
        url (str): _description_

    Yields:
        _type_: _description_
    """
    connector = UKRDCConnection(url=url)
    connector.generate_schema()
    sessionmaker = connector.create_sessionmaker()
    with sessionmaker() as session:
        create_id_generation_sequences(session)
        populate_ukrdc_tables(session, gp_info=gp_info)
        session.commit()

    print(url)

    return sessionmaker


def generate_ukrdc_test_session(gp_info: bool = False, teardown: bool = True):
    """This fixture creates a new ukrdc database with unique name. It then
    populates with existing schema, updates with new features that cupid will
    require, and populates some but not all of the lookup tables.

    When control is handed  back to the function it will delete the database.

    Yields:
        Session: session on new ukrdc
    """

    # Generate a random string as part of the URL
    random_string = str(uuid.uuid4()).replace("-", "")
    db_name = f"test_ukrdc_{random_string}"
    url = f"postgresql://postgres:postgres@localhost:5432/{db_name}"
    sessionmaker = ukrdc_sessionmaker(url=url, gp_info=gp_info)
    with sessionmaker() as session:
        yield session

    # teardown database
    if database_exists(url) and teardown:
        drop_database(url)


@pytest.fixture(scope="function")
def ukrdc_test_session():
    yield from generate_ukrdc_test_session(gp_info=False)


@pytest.fixture(scope="function")
def ukrdc_test_session_with_gp_info():
    yield from generate_ukrdc_test_session(gp_info=True)


@pytest.fixture(scope="function")
def client(ukrdc_test_session:Session):
    # Create a client to use for testing api
    app.dependency_overrides[get_session] = lambda: ukrdc_test_session
    return TestClient(app)
    