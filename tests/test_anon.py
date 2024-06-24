"""
These tests are designed to test the process of uploading and unlinking the
anonymous records. 

My (working) understanding of the process is:
- unit request opt out 
- we then follow a set of steps:
1) issue ukrr_uid to supplier  
2) append ukrr_uid to patient record 
3) orphan the ukrdcid?  
4) request a resend of their data
5) after cupid has processed the file the record should have been anonymized 
and unlinked  
"""
import os
import pytest

from sqlalchemy.orm import Session
from ukrdc_sqla.ukrdc import PatientNumber as PatientNumberORM
from ukrdc_cupid.core.store.models.ukrdc import PatientRecord
from ukrdc_cupid.core.parse.utils import load_xml_from_path
from ukrdc_cupid.core.match.identify import (
    identify_patient_feed,
    read_patient_metadata,
)


TEST_PID = "test_pid:15"
TEST_UKRDCID = "\(00)/"
UKRR_UID = "2718281818"

# We use the basic xml file and modify it to anonomise it
XML_PATH = os.path.join("tests", "xml_files", "store_tests", "test_1_anon.xml")
XML_TEST = load_xml_from_path(XML_PATH)
PATIENT_META_DATA = read_patient_metadata(XML_TEST)
UKRR_UID = PATIENT_META_DATA["MRN"][0]

@pytest.fixture(scope="function")
def ukrdc_test(ukrdc_test_session: Session): 
    # For our domain data we assume a normal record which has had a ukrr_uid
    # appended to it. I will assume for now the record doesn't get blanked at
    # by us at the point of creation of UID.  
    xml_path = os.path.join("tests", "xml_files", "store_tests", "test_1.xml")
    xml_test = load_xml_from_path(xml_path)
    commit_patient_record(ukrdc_test_session, TEST_PID, TEST_UKRDCID, XML_TEST)
    ukrdc_test_session.add(
        PatientNumberORM(
            pid = TEST_PID,
            id = f"{TEST_PID}:13",
            organization = "UKRR_UID",
            numbertype = "MRN",
            patientid = UKRR_UID
        )
    )
    ukrdc_test_session.commit()
    return ukrdc_test_session

def commit_patient_record(ukrdc_session: Session, pid, ukrdcid, xml):
    patient_record = PatientRecord(xml)
    patient_record.map_to_database(pid, ukrdcid, ukrdc_session)
    ukrdc_session.add_all(patient_record.get_orm_list())
    ukrdc_session.commit()
    return

def test_identify_new_anon(ukrdc_test: Session):
    # tests detection, matching, and validation of anonymous record
    pid, ukrdcid, investigation = identify_patient_feed(ukrdc_test, PATIENT_META_DATA)
    assert pid == TEST_PID
    assert ukrdcid == TEST_UKRDCID
    assert not investigation
