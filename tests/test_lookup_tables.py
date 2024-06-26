import os
from dotenv import load_dotenv
from ukrdc_cupid.core.store.models.lookup_tables import (
    ModalityCodes,
    RRCodes,
    RRDataDefinition,
    Locations,
)
import ukrdc_sqla.ukrdc as sqla
from rr_connection_manager import SQLServerConnection
from conftest import ukrdc_sessionmaker
from sqlalchemy_utils import database_exists
from ukrdc_cupid.core.utils import DatabaseConnection
from sqlalchemy.orm import Session, sessionmaker
import pytest


PERSISTENT_URL = "postgresql://postgres:postgres@localhost:5432/test_ukrdc_persistent"
load_dotenv()


def should_run_locally():
    run_live = os.environ.get("LIVE_DB_TESTS")
    if run_live is not None and run_live == "True":
        return True
    else:
        return False


@pytest.fixture(scope="function")
def ukrdc_test_session_persistent():
    if not database_exists(PERSISTENT_URL):
        sessionmaker = ukrdc_sessionmaker(url=PERSISTENT_URL, gp_info=True)
    else:
        sessionmaker = DatabaseConnection(url=PERSISTENT_URL).create_sessionmaker()

    with sessionmaker() as session:
        yield session


@pytest.fixture(scope="function")
def renalreg_session():
    conn = SQLServerConnection(app="renalreg_live")
    engine = conn.engine()
    session_maker = sessionmaker(engine)
    with session_maker() as session:
        yield session

'''
@pytest.mark.skipif(
    not should_run_locally(), reason="Test requires live renalreg database connection"
)
def test_load_modality_codes(
    renalreg_session: Session, ukrdc_test_session_persistent: Session
):
    """Test load codes from the ukrr database to

    Args:
        renalreg_session (Session): _description_
        ukrdc_test_session_persistent (Session): _description_
    """

    # sync table in ukrdc from ukrr
    modality_codes = ModalityCodes(renalreg_session, ukrdc_test_session_persistent)
    modality_codes.sync_table_from_renalreg()

    # change the haemodialysis code
    haemo_code = ukrdc_test_session_persistent.get(sqla.ModalityCodes, "1")
    haemo_code_desc = haemo_code.registry_code_desc
    haemo_code.registry_code_desc = haemo_code_desc + " now out of sync"
    ukrdc_test_session_persistent.commit()

    # sync again and check we arrive back where we started
    modality_codes.sync_table_from_renalreg()
    haemo_code = ukrdc_test_session_persistent.get(sqla.ModalityCodes, "1")
    assert haemo_code_desc == haemo_code.registry_code_desc

    """
    print("[=   ]")
    rr_codes = RRCodes(renalreg_session, ukrdc_test_session_persistent)
    rr_codes.sync_table_from_renalreg()

    print("[]==  ]")
    rr_codes = RRDataDefinition(renalreg_session, ukrdc_test_session_persistent)
    rr_codes.sync_table_from_renalreg()

    print("[=== ]")
    rr_codes = Locations(renalreg_session, ukrdc_test_session_persistent)
    rr_codes.sync_table_from_renalreg()
    """
'''