import os
from ukrdc_cupid.core.store.models.lookup_tables import (
    ModalityCodes,
    RRCodes,
    RRDataDefinition,
    Locations,
)
import ukrdc_sqla.ukrdc as sqla
from ukrdc_cupid.core.utils import UKRDCConnection, UKRRConnection
from sqlalchemy.orm import Session
import pytest


#PERSISTENT_URL = "postgresql://postgres:postgres@localhost:5432/test_ukrdc_persistent"


def should_run_locally():
    run_live = os.environ.get("LIVE_DB_TESTS")
    if run_live is not None and run_live == "True":
        return True
    else:
        return False


@pytest.fixture(scope="function")
def ukrdc_test_session_persistent():
    connector = UKRDCConnection()
    if connector.engine is not None:
        connector.generate_schema()
        sessionmaker = connector.create_sessionmaker()
        with sessionmaker() as session:
            yield session
    else: 
        yield None
    


@pytest.fixture(scope="function")
def renalreg_session():
    try:
        connector = UKRRConnection()
    except:
        yield None
    else:
        sessionmaker = connector.create_sessionmaker()
        with sessionmaker() as session:
            yield session

def test_load_modality_codes(
    renalreg_session: Session, ukrdc_test_session_persistent: Session
):
    """Test load codes from the ukrr database to

    Args:
        renalreg_session (Session): _description_
        ukrdc_test_session_persistent (Session): _description_
    """
    if renalreg_session is not None:
        # sync table in ukrdc from ukrr
        ModalityCodes()
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

def test_load_rr_codes(
    renalreg_session: Session, ukrdc_test_session_persistent: Session
):
    """
    """
    if renalreg_session is not None:
        rr_codes = RRCodes(
            renalreg_session=renalreg_session, 
            ukrdc_session=ukrdc_test_session_persistent
        )
        rr_codes.sync_table_from_renalreg()
        assert True

def test_load_location_codes(
    renalreg_session: Session, ukrdc_test_session_persistent: Session 
):
    """

    Args:
        renalreg_session (Session): _description_
        ukrdc_test_session_persistent (Session): _description_
    """
    if renalreg_session is not None:
        locations = Locations(
            renalreg_session=renalreg_session, 
            ukrdc_session=ukrdc_test_session_persistent
        )
        locations.sync_table_from_renalreg()
        assert True


def test_rr_data_definition(
    renalreg_session: Session, ukrdc_test_session_persistent: Session     
):
    if renalreg_session is not None:
        rr_data_definition = RRDataDefinition(renalreg_session, ukrdc_test_session_persistent)
        rr_data_definition.sync_table_from_renalreg()
        assert True