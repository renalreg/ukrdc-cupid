""" Testing philosophy here is to create a middle ground between unit testing
and black box testing. Fundimentally the xml files are input which triggers a
change to the state of the database, or alternatively causes an error, or an 
investigation. We then use xml files load them and check they trigger the
desired change to the database. To get more in the spirit of unit tests, xml
files target specific areas of the code. 

xml files used:
test_1.xml

Still to do: 
1) test removal of elements
2) ensure full coverage of all possible xml items 
"""

from ukrdc_cupid.core.store.models.ukrdc import PatientRecord
from ukrdc_cupid.core.parse.utils import load_xml_from_path
from ukrdc_cupid.core.utils import DatabaseConnection
from sqlalchemy.orm import Session
import os
import pytest

TEST_PID = "test_pid:731"
TEST_UKRDCID = "test_ukrdc:543"


@pytest.fixture(scope="function")
def ukrdc_test():
    """
    Create a test database to check patient demographic and identiey based
    stuff.
    """
    ukrdc3_session = DatabaseConnection().create_session(clean=True, populate_tables=False)
    yield ukrdc3_session
    ukrdc3_session.close()

@pytest.fixture(scope="function")
def patient_record(ukrdc_test:Session):
    xml_test_1 = load_xml_from_path(
        os.path.join("tests","xml_files","store_tests","test_1.xml")
    )
    patient_record = PatientRecord(xml_test_1)
    patient_record.map_to_database(TEST_PID, TEST_UKRDCID,ukrdc_test)

    return patient_record


def test_patient_record(patient_record:PatientRecord):

    patient_record_orm = False
    for orm_object in patient_record.get_orm_list():
        if orm_object.__tablename__ == "patientrecord":
            patient_record_orm = orm_object
            break

    assert patient_record_orm
    assert patient_record_orm.pid == TEST_PID
    assert patient_record_orm.ukrdcid == TEST_UKRDCID
    assert patient_record_orm.localpatientid == "AAA111B"
    
    assert patient_record_orm.sendingfacility == patient_record.xml.sending_facility.value
    assert patient_record_orm.sendingextract == patient_record.xml.sending_extract.value


def test_patient(patient_record:PatientRecord):
    patient_orm = False
    for orm_object in patient_record.get_orm_list():
        if orm_object.__tablename__ == "patient":
            patient_orm = orm_object
            break

    assert patient_orm
    assert patient_orm.pid == patient_orm.id
    assert patient_orm.pid == TEST_PID

    patient_xml = patient_record.xml.patient
    # check attributes of orm objects 
    assert patient_orm.birthtime == patient_xml.birth_time.to_datetime()
    assert patient_orm.countryofbirth == patient_xml.country_of_birth
    assert patient_orm.death == patient_xml.death
    assert patient_orm.deathtime == patient_xml.death_time.to_datetime()
    assert patient_orm.gender == patient_xml.gender.value


def test_name(patient_record:PatientRecord):
    name_orm = False
    for orm_object in patient_record.get_orm_list():
        if orm_object.__tablename__ == "name":
            name_orm = orm_object
            break

    name_xml = patient_record.xml.patient.names.name[0]

    assert name_orm.pid == TEST_PID
    assert name_orm.prefix == name_xml.prefix
    assert name_orm.given == name_xml.given
    assert name_orm.family == name_xml.family
    assert name_orm.othergivennames == name_xml.other_given_names
    assert name_orm.suffix == name_xml.suffix


def test_contact_detail(patient_record:PatientRecord):
    contact_detail_orm = False
    for orm_object in patient_record.get_orm_list():
        if orm_object.__tablename__ == "contactdetail":
            contact_detail_orm = orm_object
            break
    assert contact_detail_orm

    contact_detail_xml = patient_record.xml.patient.contact_details.contact_detail[0]

    idx_singular = 0
    assert contact_detail_orm.idx == idx_singular
    assert contact_detail_orm.pid == TEST_PID
    assert contact_detail_orm.id == f"{TEST_PID}:{idx_singular}"

    assert contact_detail_orm.value == contact_detail_xml.value
    assert contact_detail_orm.contactuse == contact_detail_xml.use.value


def test_address(patient_record:PatientRecord):
    address_orm = False
    for orm_object in patient_record.get_orm_list():
        if orm_object.__tablename__ == "address":
            address_orm = orm_object
            break

    assert address_orm
    address_xml = patient_record.xml.patient.addresses.address[0]

    assert address_orm.fromtime == address_xml.from_time.to_datetime()
    assert address_orm.totime == address_xml.to_time.to_datetime()
    assert address_orm.street == address_xml.street
    assert address_orm.town == address_xml.town
    assert address_orm.county == address_xml.county
    assert address_orm.postcode == address_xml.postcode

    # Check country attributes
    assert address_orm.countrycodestd == address_xml.country.coding_standard.value
    assert address_orm.countrycode == address_xml.country.code
    assert address_orm.countrydesc == address_xml.country.description


def test_family_doctor(patient_record:PatientRecord):
    family_doctor_orm = False
    for orm_object in patient_record.get_orm_list():
        if orm_object.__tablename__ == "familydoctor":
            family_doctor_orm = orm_object
            break
    
    assert family_doctor_orm

    family_doctor_xml = patient_record.xml.patient.family_doctor

    assert family_doctor_orm.id == TEST_PID
    assert family_doctor_orm.gppracticeid == family_doctor_xml.gppractice_id
    assert family_doctor_orm.gpid == family_doctor_xml.gpid
    assert family_doctor_orm.gpname == family_doctor_xml.gpname
    #assert address or whatever else