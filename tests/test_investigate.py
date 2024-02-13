"""
The investigate tests should cover any instance where an investigation is
raised the logic for this can be found here: 
https://renalregistry.atlassian.net/wiki/x/BQAfkw

Each route by which a file can be rejected or an investigation raised for
should have a corresponding test. When a file is rejected a pid and ukrdcid
won't be returned however they will be recorded in the investigations db.
"""


import pytest
import os
from datetime import timedelta

from sqlalchemy.orm import Session
from ukrdc_cupid.core.parse.utils import load_xml_from_path
from ukrdc_cupid.core.store.models.ukrdc import PatientRecord
from ukrdc_cupid.core.investigate.utils import ISSUE_PICKLIST
from ukrdc_cupid.core.match.identify import (
    identify_patient_feed,
    read_patient_metadata,
)
from ukrdc_cupid.core.utils import DatabaseConnection



TEST_PID = "test_pid:731"
TEST_UKRDCID = "\(00)/"
XML_PATH = os.path.join("tests","xml_files","store_tests","test_0.xml")
XML_TEST = load_xml_from_path(XML_PATH)
PATIENT_META_DATA = read_patient_metadata(XML_TEST)
POSSIBLE_ISSUES = [issuetype[0] for issuetype in ISSUE_PICKLIST]

@pytest.fixture(scope="function")
def ukrdc_test():
    connector = DatabaseConnection(env_prefix="UKRDC")
    session = connector.create_session(clean=True, populate_tables=False)
    commit_patient_record(session, TEST_PID, TEST_UKRDCID, XML_TEST)
    yield session
    session.close()

def commit_patient_record(ukrdc_session:Session, pid, ukrdcid, xml):
    patient_record = PatientRecord(xml)  
    patient_record.map_to_database(pid, ukrdcid, ukrdc_session)
    ukrdc_session.add_all(patient_record.get_orm_list())
    ukrdc_session.commit()
    return 



def test_ambiguous_pid(ukrdc_test:Session):
    """One of the basic investigations arises if the matching flags that there
    are multiple records that could be matched to an incoming files due to
    because the national identifier matches multiple domain records.

    Args:
        ukrdc_test (Session): _description_
    """
    duplicate_pid = f"{TEST_PID}:duplicate"
    commit_patient_record(ukrdc_test, duplicate_pid, TEST_UKRDCID, XML_TEST)
    pid, ukrdcid, investigation = identify_patient_feed(ukrdc_test, PATIENT_META_DATA)
    assert not pid
    assert not ukrdcid 
    assert investigation.issue_id in POSSIBLE_ISSUES

    for patient in investigation.patients:
        assert patient.pid in [TEST_PID, duplicate_pid]
        assert patient.ukrdcid == TEST_UKRDCID

def test_demog_validation(ukrdc_test:Session):
    """
    One layer of validation the matches go through is a check to ensure the
    dob of the incoming file matches the domain. If not an investigation will
    be raised. The MRN can be changed by sending two files one where it has
    """

    modified_metadata = PATIENT_META_DATA.copy()
    modified_metadata["birth_time"] = modified_metadata["birth_time"] + timedelta(days = 1)
    pid, ukrdcid, investigation = identify_patient_feed(ukrdc_test, modified_metadata)
    assert not pid
    assert not ukrdcid
    assert investigation.issue_id in POSSIBLE_ISSUES
    assert investigation.issue_id == 1

def test_mrn_matching(ukrdc_test:Session):
    """The NI and MRN are both matched to patient records in the database. If
    they don't match to one unique patient record a work item will be flagged


    Args:
        ukrdc_test (Session): _description_
    """
    modified_metadata = PATIENT_META_DATA.copy()
    modified_metadata["MRN"] = ["BBB111B", "LOCALHOSP"]
    pid, ukrdcid, investigation = identify_patient_feed(ukrdc_test, modified_metadata)
    
    assert 1==1

