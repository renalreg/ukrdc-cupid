from sqlalchemy.orm import Session
from conftest import create_test_session, TEST_DB_URL
from ukrdc_cupid.core.parse.utils import load_xml_from_path
from ukrdc_cupid.core.store.models.ukrdc import PatientRecord
from ukrdc_cupid.core.match.identify import (
    identify_patient_feed,
    read_patient_metadata,
    identify_across_ukrdc,
)
from ukrdc_cupid.core.utils import DatabaseConnection
from sqlalchemy import select
from ukrdc_sqla.ukrdc import PatientNumber
import pytest
import os

TEST_PID = "test_pid:731"
TEST_UKRDCID = "\(00)/"
XML_PATH = os.path.join("tests","xml_files","store_tests","test_0.xml")
XML_TEST = load_xml_from_path(XML_PATH)
PATIENT_META_DATA = read_patient_metadata(XML_TEST)

@pytest.fixture(scope="function")
def ukrdc_test():
    session = DatabaseConnection().create_session(clean=True, populate_tables=False)
    commit_patient_record(session, TEST_PID, TEST_UKRDCID, XML_TEST)
    yield session
    session.close()


def commit_patient_record(ukrdc_session:Session, pid, ukrdcid, xml):
    patient_record = PatientRecord(xml)  
    patient_record.map_to_database(pid, ukrdcid, ukrdc_session)
    ukrdc_session.add_all(patient_record.get_orm_list())
    ukrdc_session.commit()
    return 

def test_match_ni(ukrdc_test:Session):
    """The primary type of matching. A patient in an incoming file is matched
    to a domain patient record on the national identifier. It then gets
    verified on MRN and dob. 
    """
    pid, ukrdcid, investigation = identify_patient_feed(ukrdc_test, PATIENT_META_DATA)
    
    assert pid == TEST_PID
    assert ukrdcid == TEST_UKRDCID 
    assert not investigation

def test_overwrite_with_chi_no(ukrdc_test:Session):
    """Test the linking of record to existing scottish record if a chi number
    is added into the file. This also tests the process of overwriting a NI.
    In reality I imagine you would just add an extra NI rather than
    overwriting. 
    """
    xml_path = os.path.join("tests","xml_files","store_tests","test_3.xml")
    xml_test = load_xml_from_path(xml_path)
    meta_data = read_patient_metadata(xml_test)
    pid, ukrdcid, investigation = identify_patient_feed(ukrdc_test, meta_data)
    
    assert pid == TEST_PID
    assert ukrdcid == TEST_UKRDCID 
    assert not investigation

    # plug file into database
    patient_record = PatientRecord(xml_test)  
    patient_record.map_to_database(pid, ukrdcid, ukrdc_test)
    ukrdc_test.commit()

    stmt = select(PatientNumber).where(PatientNumber.pid == TEST_PID)
    query_result = ukrdc_test.execute(stmt).fetchall()
    
    new_ni = [result[0] for result in query_result if result[0].numbertype == "NI"]
    contains_chi = False
    for number in new_ni:
        if number.organization == "CHI":
            contains_chi = True
    
    assert contains_chi