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

from conftest import ukrdc3_session
from ukrdc_cupid.core.store.models.ukrdc import PatientRecord
from ukrdc_cupid.core.parse.utils import load_xml_from_path
from typing import Tuple
import ukrdc_xsdata.ukrdc as xsd # type: ignore
import os
import pytest

TEST_PID = "test_pid:731"
TEST_UKRDCID = "test_ukrdc:543"

@pytest.fixture(scope="function")
def test_patient_objects():
    xml_test_1 = load_xml_from_path(
        os.path.join("tests","xml_files","store_tests","test_1.xml")
    )
    patient_record = PatientRecord(xml_test_1)
    patient_record.map_to_database(TEST_PID, TEST_UKRDCID, ukrdc3_session)
    test_orms = {}
    for orm_object in patient_record.get_orm_list():
        key = orm_object.__tablename__
        if key in test_orms:
            test_orms[key].append(orm_object) 
        else:
            test_orms[key] = [orm_object]

    return xml_test_1, test_orms


def test_patient_record(test_patient_objects:Tuple[xsd.PatientRecord,dict]):
    patient_record_xml, orms = test_patient_objects
    patient_record_orm = orms["patientrecord"][0]
    
    assert patient_record_orm.pid == TEST_PID
    assert patient_record_orm.ukrdcid == TEST_UKRDCID
    assert patient_record_orm.localpatientid == "AAA111B"
    
    assert patient_record_orm.sendingfacility == patient_record_xml.sending_facility.value
    assert patient_record_orm.sendingextract == patient_record_xml.sending_extract.value


def test_patient(test_patient_objects:Tuple[xsd.PatientRecord,dict]):
    patient_record_xml, orms = test_patient_objects
    patient_orm = orms["patient"][0]
    patient_xml = patient_record_xml.patient

    assert patient_orm.pid == patient_orm.id
    assert patient_orm.pid == TEST_PID

    # check attributes of orm objects 
    assert patient_orm.birthtime == patient_xml.birth_time.to_datetime()
    assert patient_orm.countryofbirth == patient_xml.country_of_birth
    assert patient_orm.death == patient_xml.death
    assert patient_orm.deathtime == patient_xml.death_time.to_datetime()
    assert patient_orm.gender == patient_xml.gender.value


def test_name(test_patient_objects: Tuple[xsd.PatientRecord, dict]):
    patient_record_xml, orms = test_patient_objects
    name_orm = orms["name"][0]
    name_xml = patient_record_xml.patient.names.name[0]

    assert name_orm.pid == TEST_PID
    assert name_orm.prefix == name_xml.prefix
    assert name_orm.given == name_xml.given
    assert name_orm.family == name_xml.family
    assert name_orm.othergivennames == name_xml.other_given_names
    assert name_orm.suffix == name_xml.suffix


def test_contact_detail(test_patient_objects: Tuple[xsd.PatientRecord, dict]):
    patient_record_xml, orms = test_patient_objects
    contact_detail_orm = orms["contactdetail"][0]
    contact_detail_xml = patient_record_xml.patient.contact_details.contact_detail[0]

    idx_singular = 0
    assert contact_detail_orm.idx == idx_singular
    assert contact_detail_orm.pid == TEST_PID
    assert contact_detail_orm.id == f"{TEST_PID}:{idx_singular}"

    assert contact_detail_orm.value == contact_detail_xml.value
    assert contact_detail_orm.contactuse == contact_detail_xml.use.value


def test_address(test_patient_objects: Tuple[xsd.PatientRecord, dict]):
    patient_record_xml, orms = test_patient_objects
    address_orm = orms["address"][0]
    address_xml = patient_record_xml.patient.addresses.address[0]

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


def test_family_doctor(test_patient_objects: Tuple[xsd.PatientRecord, dict]):
    patient_record_xml, orms = test_patient_objects
    family_doctor_orm = orms["familydoctor"][0]
    family_doctor_xml = patient_record_xml.patient.family_doctor

    assert family_doctor_orm.id == TEST_PID
    assert family_doctor_orm.gppracticeid == family_doctor_xml.gppractice_id
    assert family_doctor_orm.gpid == family_doctor_xml.gpid
    assert family_doctor_orm.gpname == family_doctor_xml.gpname
    #assert address or whatever else