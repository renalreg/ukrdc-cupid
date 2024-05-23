from ukrdc_cupid.core.store.models.lookup_tables import ModalityCodes, RRCodes, RRDataDefinition, Locations 
from rr_connection_manager import SQLServerConnection
from conftest import ukrdc_sessionmaker
from sqlalchemy_utils import database_exists
from ukrdc_cupid.core.utils import DatabaseConnection
from sqlalchemy.orm import Session, sessionmaker
import pytest

PERSISTENT_URL = "postgresql://postgres:postgres@localhost:5432/test_ukrdc_persistent"

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
    engine = conn.engine(isolation_level = "READ UNCOMMITTED")
    session_maker = sessionmaker(engine)
    with session_maker() as session:
        yield session

def test_load_rr_codes(renalreg_session:Session, ukrdc_test_session_persistent:Session):
    """Test load codes from the ukrr database to 

    Args:
        renalreg_session (Session): _description_
        ukrdc_test_session_persistent (Session): _description_
    """
    modality_codes = ModalityCodes(renalreg_session, ukrdc_test_session_persistent)
    modality_codes.sync_table_from_renalreg()

    print("[=   ]")
    rr_codes = RRCodes(renalreg_session, ukrdc_test_session_persistent)
    rr_codes.sync_table_from_renalreg()

    print("[]==  ]")
    rr_codes = RRDataDefinition(renalreg_session, ukrdc_test_session_persistent)
    rr_codes.sync_table_from_renalreg()

    print("[=== ]")
    rr_codes = Locations(renalreg_session, ukrdc_test_session_persistent)
    rr_codes.sync_table_from_renalreg()

    assert True