"""
The investigate tests should cover any instance where an investigation is
raised the logic for this can be found here: 
https://renalregistry.atlassian.net/wiki/x/BQAfkw

Each route by which a file can be rejected or an investigation raised for
should have a corresponding test. When a file is rejected a pid and ukrdcid
won't be returned however they will be recorded in the investigations db.

if investigations are raised with matching a feed the file is not inserted. 
when it comes to matching with the ukrdcid this is fairly straight forward to
reverse so the record is inserted but a new ukrdcid is produced. This can be
easily changed manually.
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
    identify_across_ukrdc
)
from ukrdc_cupid.core.utils import DatabaseConnection


TEST_PID = "test_pid:731"
TEST_UKRDCID = "\(00)/"
XML_PATH = os.path.join("tests", "xml_files", "store_tests", "test_0.xml")
XML_TEST = load_xml_from_path(XML_PATH)
PATIENT_META_DATA = read_patient_metadata(XML_TEST)
POSSIBLE_ISSUES = [issuetype[0] for issuetype in ISSUE_PICKLIST]


@pytest.fixture(scope="function")
def ukrdc_test(ukrdc_test_session: Session):
    commit_patient_record(ukrdc_test_session, TEST_PID, TEST_UKRDCID, XML_TEST)
    return ukrdc_test_session


def commit_patient_record(ukrdc_session: Session, pid, ukrdcid, xml):
    patient_record = PatientRecord(xml)
    patient_record.map_to_database(pid, ukrdcid, ukrdc_session)
    ukrdc_session.add_all(patient_record.get_orm_list())
    ukrdc_session.commit()
    return


def test_ambiguous_pid(ukrdc_test: Session):
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
    assert investigation.issue.issue_id in POSSIBLE_ISSUES

    for patient in investigation.patients:
        assert patient.pid in [TEST_PID, duplicate_pid]
        assert patient.ukrdcid == TEST_UKRDCID


def test_demog_validation(ukrdc_test: Session):
    """
    One layer of validation the matches go through is a check to ensure the
    dob of the incoming file matches the domain. If not an investigation will
    be raised. The MRN can be changed by sending two files one where it has
    """

    modified_metadata = PATIENT_META_DATA.copy()
    modified_metadata["birth_time"] = modified_metadata["birth_time"] + timedelta(
        days=1
    )
    pid, ukrdcid, investigation = identify_patient_feed(ukrdc_test, modified_metadata)
    assert not pid
    assert not ukrdcid
    assert investigation.issue.issue_id in POSSIBLE_ISSUES
    assert investigation.issue.issue_id == 1


def test_no_mrn_matching(ukrdc_test:Session):
    """

    Args:
        ukrdc_test (Session): _description_
    """

    modified_metadata = PATIENT_META_DATA.copy()
    modified_metadata["MRN"] = ["blahblah", "LOCALHOSP"]
    
    pid, ukrdcid, investigation = identify_patient_feed(ukrdc_test, modified_metadata)

    assert not pid 
    assert not ukrdcid
    assert investigation.issue.issue_id in POSSIBLE_ISSUES
    assert investigation.issue.issue_id == 2


def test_multiple_matches(ukrdc_test:Session):
    """Test case when multiple persitent feeds match incoming

    Args:
        ukrdc_test (Session): _description_
    """

    duplicate_pid = f"duplicate"
    duplicate_ukrdcid = f"duplicate"
    commit_patient_record(ukrdc_test, duplicate_pid, duplicate_ukrdcid, XML_TEST)
    pid, ukrdcid, investigation = identify_patient_feed(ukrdc_test, PATIENT_META_DATA)
    
    assert not pid 
    assert not ukrdcid
    assert investigation.issue.issue_id in POSSIBLE_ISSUES
    assert investigation.issue.issue_id == 3
    assert len(investigation.patients) > 1



def test_mrn_matching(ukrdc_test: Session):
    """The NI and MRN are both matched to patient records in the database. If
    they don't match to one unique patient record a work item will be flagged

    Args:
        ukrdc_test (Session): _description_
    """

    mrn_different = "BBB111B"
    new_pid = "dip_wen"
    new_ukrdcid = "!(00)!"
    xml = XML_TEST
    xml.patient.patient_numbers.patient_number[0].number = mrn_different
    commit_patient_record(ukrdc_test, new_pid, new_ukrdcid, xml)


    modified_metadata = PATIENT_META_DATA.copy()
    modified_metadata["MRN"] = [mrn_different, "LOCALHOSP"]
    pid, ukrdcid, investigation = identify_patient_feed(ukrdc_test, modified_metadata)



    assert not pid 
    assert not ukrdcid
    assert investigation.issue.issue_id in POSSIBLE_ISSUES
    assert investigation.issue.issue_id == 4

def test_demog_invalid_ukrdcid(ukrdc_test:Session):
    """
    Investigation raise when feed is assigned a ukrdcid but the demographics
    don't match. 

    Args:
        ukrdc_test (Session): _description_
    """
    modified_metadata = PATIENT_META_DATA.copy()
    modified_metadata["birth_time"] = modified_metadata["birth_time"] + timedelta(
        days=1
    )

    ukrdcid, investigation = identify_across_ukrdc(ukrdc_test,patient_info=modified_metadata)
    assert not ukrdcid
    assert investigation.issue.issue_id in POSSIBLE_ISSUES
    assert investigation.issue.issue_id == 5


def test_multiple_matches_ukrdcid(ukrdc_test:Session):
    """Test case where there are multiple matches to the same ukrdcid. 
    The behaviour here is something like. 1) Create work item, 2) mint new 
    ukrdcid 3) Future files will get merged in the area of the code which 
    identifies feeds.

    Args:
        ukrdc_test (Session): _description_
    """
    duplicate_pid = f"duplicate"
    duplicate_ukrdcid = f"duplicate"
    commit_patient_record(ukrdc_test, duplicate_pid, duplicate_ukrdcid, XML_TEST)

    ukrdcid, investigation = identify_across_ukrdc(ukrdc_test,patient_info=PATIENT_META_DATA)
    
    assert not ukrdcid
    assert investigation.issue.issue_id in POSSIBLE_ISSUES
    assert investigation.issue.issue_id == 6