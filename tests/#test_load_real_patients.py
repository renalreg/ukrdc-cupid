"""
Getting into danger territory here but I think it would be good to have an area
for testing with real patient data. Need to be very sure nothing is getting
committed though. Real patient data should only ever end up in the folder
.xml_to_load which is in the .gitignore so hopefully safe. 

Rather than create and drop a dummy database we have a persistent db this
allows the interrogate the effect of loading up the data. This is a cupid 
complient ukrdc database which is automatically created with the utilities in
this repo.

Since these results are being run against a persistent database they might not
necessarily behave in a consistent way.
"""

import glob
import pytest
import copy

from ukrdc_cupid.core.investigate.models import XmlFile
from ukrdc_cupid.core.parse.utils import load_xml_from_path
from ukrdc_cupid.core.general import process_file_from_path
from ukrdc_cupid.core.utils import UKRDCConnection
#from ukrdc_cupid.core.match.identify import read_patient_metadata

from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists
from sqlalchemy import select
import ukrdc_sqla.ukrdc as orm_objects

from xsdata.models.datatype import XmlDateTime
from xsdata.formats.dataclass.serializers import XmlSerializer

serializer = XmlSerializer()
XML_DIRECTORY = ".xml_to_load/*.xml"

@pytest.fixture(scope="function")
def ukrdc_test_session_persistent():
    connector = UKRDCConnection()
    if not database_exists(connector.url):
        connector.generate_schema(gp_info=True)
        sessionmaker = connector.create_sessionmaker()
    else:
        sessionmaker = connector.create_sessionmaker()

    with sessionmaker() as session:
        yield session


@pytest.mark.parametrize("xml_file", glob.glob(XML_DIRECTORY))
def test_load_xml_file(ukrdc_test_session_persistent: Session, xml_file: str):
    # we start  by just loading to see what happens
    xml_object = load_xml_from_path(xml_file)
    investigation = process_file_from_path(
        xml_object,
        ukrdc_session=ukrdc_test_session_persistent,
    )

    assert not investigation


@pytest.mark.parametrize("xml_file", glob.glob(XML_DIRECTORY))
def test_dob_validation(ukrdc_test_session_persistent: Session, xml_file: str):
    # Now we deliberately mess a few things up. We start by changing the
    # demographics to break the verification of the match at the moment
    # there are no uniqueness constraints or check to see if the system has
    # seen the problematic files already
    xml_object = load_xml_from_path(xml_file)
    investigation = process_file_from_path(
        xml_object,
        ukrdc_session=ukrdc_test_session_persistent,
    )

    assert not investigation

    xml_altered = copy.deepcopy(xml_object)
    day = xml_altered.patient.birth_time.day
    month = xml_altered.patient.birth_time.month
    year = xml_altered.patient.birth_time.year

    if day > 1:
        xml_altered.patient.birth_time = XmlDateTime(
            day=day - 1, month=month, year=year, hour=0, minute=0, second=0
        )
    else:
        xml_altered.patient.birth_time = XmlDateTime(
            day=day + 1, month=month, year=year, hour=0, minute=0, second=0
        )

    investigation = process_file_from_path(
        xml_altered, ukrdc_session=ukrdc_test_session_persistent, file_path=xml_file
    )

    assert investigation

    issue = investigation.issue 

    assert issue.issue_id == 1
    assert issue.filename == xml_file

    query_xml = select(XmlFile).where(XmlFile.id == issue.xml_file_id)
    xml_orm = ukrdc_test_session_persistent.execute(query_xml).scalar_one_or_none()
    assert xml_orm is not None
    assert xml_orm.file == serializer.render(xml_altered)
    issue.is_blocking = False
    ukrdc_test_session_persistent.add(issue)
    ukrdc_test_session_persistent.commit()


# @pytest.mark.parametrize("xml_file", glob.glob(XML_DIRECTORY))
def test_wrong_nhs_number(ukrdc_test_session_persistent: Session):
    # The matching is verified using the NI if a match is made on the MRN but
    # not the NI it should trigger an error

    files = glob.glob(XML_DIRECTORY)
    if len(files) > 0: # turn off test if running in github actions
        for file in files:
            xml_object = load_xml_from_path(file)
            investigation = process_file_from_path(
                xml_object,
                ukrdc_session=ukrdc_test_session_persistent,
            )
            assert not investigation


        patient_numbers = ukrdc_test_session_persistent.scalars(
            select(orm_objects.PatientNumber).limit(10)
        )

        
        xml_altered = copy.deepcopy(xml_object)

        for number in xml_altered.patient.patient_numbers.patient_number:
            if number.organization.value == "NHS":
                for db_number in patient_numbers.all():
                    if db_number.organization == "NHS":
                        if db_number.patientid != number.number:
                            # we set the nhs number to match a different record
                            number.number = db_number.patientid
                            break
                break



        # now we run the files back through to flag an error
        investigation = process_file_from_path(
            xml_altered,
            ukrdc_session=ukrdc_test_session_persistent,
        )

        assert investigation
        
        issue = investigation.issue 
        assert issue.issue_id == 4
        assert len(investigation.patients) > 1

        query_xml = select(XmlFile).where(XmlFile.id == issue.xml_file_id)
        xml_orm = ukrdc_test_session_persistent.execute(query_xml).scalar_one_or_none()
        assert xml_orm is not None
        assert xml_orm.file == serializer.render(xml_altered)
        issue.is_blocking = False
        ukrdc_test_session_persistent.add(issue)
        ukrdc_test_session_persistent.commit()