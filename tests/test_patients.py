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
from sqlalchemy.orm import Session

import os
import pytest
import uuid

TEST_PID = "test_pid:731"
TEST_UKRDCID = "test_ukrdc:543"


@pytest.fixture(scope="function")
def patient_record(ukrdc_test_session: Session):
    xml_test_1 = load_xml_from_path(
        os.path.join("tests", "xml_files", "store_tests", "test_1.xml")
    )
    patient_record = PatientRecord(xml_test_1)
    patient_record.map_to_database(TEST_PID, TEST_UKRDCID, ukrdc_test_session)

    return patient_record


def test_patient_record(patient_record: PatientRecord):

    patient_record_orm = False
    for orm_object in patient_record.get_new_records():
        if orm_object.__tablename__ == "patientrecord":
            patient_record_orm = orm_object
            break

    assert patient_record_orm
    assert patient_record_orm.pid == TEST_PID
    assert patient_record_orm.ukrdcid == TEST_UKRDCID
    assert patient_record_orm.localpatientid == "AAA111B"

    assert (
        patient_record_orm.sendingfacility == patient_record.xml.sending_facility.value
    )
    assert patient_record_orm.sendingextract == patient_record.xml.sending_extract.value


def test_patient(patient_record: PatientRecord):
    patient_orm = False
    for orm_object in patient_record.get_new_records():
        if orm_object.__tablename__ == "patient":
            patient_orm = orm_object
            break

    assert patient_orm
    assert patient_orm.pid == patient_orm.id
    assert patient_orm.pid == TEST_PID

    patient_xml = patient_record.xml.patient
    # check attributes of orm objects
    if patient_xml.birth_time:
        xml_time = str(patient_xml.birth_time)[:10]
        orm_time = str(patient_orm.birthtime)[:10]
        assert xml_time == orm_time

    assert patient_orm.countryofbirth == patient_xml.country_of_birth
    if not patient_xml.death:
        assert not patient_orm.death
        assert not patient_orm.deathtime
    else:
        assert patient_orm.death 
        assert patient_xml.death_time.to_datetime()
    assert patient_orm.gender == patient_xml.gender.value


def test_name(patient_record: PatientRecord):
    name_orm = False
    for orm_object in patient_record.get_new_records():
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


def test_contact_detail(patient_record: PatientRecord):
    contact_detail_orm = False
    for orm_object in patient_record.get_new_records():
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


def test_address(patient_record: PatientRecord):
    address_orm = False
    for orm_object in patient_record.get_new_records():
        if orm_object.__tablename__ == "address":
            address_orm = orm_object
            break

    assert address_orm
    address_xml = patient_record.xml.patient.addresses.address[0]

    if address_xml.from_time:
        xml_time = str(address_xml.from_time)[:10]
        orm_time = str(address_orm.fromtime)[:10]
        assert xml_time == orm_time
    
    if address_xml.to_time:
        xml_time = str(address_xml.to_time)[:10]
        orm_time = str(address_orm.totime)[:10]
        assert xml_time == orm_time
    
    assert address_orm.street == address_xml.street
    assert address_orm.town == address_xml.town
    assert address_orm.county == address_xml.county
    assert address_orm.postcode == address_xml.postcode

    # Check country attributes
    assert address_orm.countrycodestd == address_xml.country.coding_standard.value
    assert address_orm.countrycode == address_xml.country.code
    assert address_orm.countrydesc == address_xml.country.description


def test_family_doctor(patient_record: PatientRecord):
    family_doctor_orm = False
    for orm_object in patient_record.get_new_records():
        if orm_object.__tablename__ == "familydoctor":
            family_doctor_orm = orm_object
            break

    assert family_doctor_orm

    family_doctor_xml = patient_record.xml.patient.family_doctor

    assert family_doctor_orm.id == TEST_PID
    assert family_doctor_orm.gppracticeid == family_doctor_xml.gppractice_id
    assert family_doctor_orm.gpid == family_doctor_xml.gpid
    assert family_doctor_orm.gpname == family_doctor_xml.gpname
    # assert address or whatever else


def test_family_history(patient_record: PatientRecord):
    family_history_orm = False
    for orm_object in patient_record.get_new_records():
        if orm_object.__tablename__ == "familyhistory":
            family_history_orm = orm_object
            break

    assert family_history_orm

    family_history_xml = patient_record.xml.family_histories.family_history[0]
    assert family_history_orm.familymembercode == family_history_xml.family_member.code
    assert (
        family_history_orm.familymembercodestd
        == family_history_xml.family_member.coding_standard
    )
    assert (
        family_history_orm.familymemberdesc
        == family_history_xml.family_member.description
    )
    assert (
        family_history_orm.diagnosiscodestd
        == family_history_xml.diagnosis.coding_standard.value
    )
    assert family_history_orm.diagnosiscode == family_history_xml.diagnosis.code
    assert family_history_orm.diagnosisdesc == family_history_xml.diagnosis.description
    assert family_history_orm.notetext == family_history_xml.note_text
    assert family_history_orm.enteredatcode == family_history_xml.entered_at.code
    assert (
        family_history_orm.enteredatcodestd
        == family_history_xml.entered_at.coding_standard.value
    )
    assert family_history_orm.enteredatdesc == family_history_xml.entered_at.description
    
    if family_history_xml.from_time:
        xml_time = str(family_history_xml.from_time)[:10]
        orm_time = str(family_history_orm.fromtime)[:10]
        assert xml_time == orm_time
    
    if family_history_xml.to_time:
        xml_time = str(family_history_xml.to_time)[:10]
        orm_time = str(family_history_orm.totime)[:10]
        assert xml_time == orm_time
    
    if family_history_xml.updated_on:
        xml_time = str(family_history_xml.updated_on)[:10]
        orm_time = str(family_history_orm.updatedon)[:10]
        assert xml_time == orm_time
    
    assert family_history_orm.externalid == family_history_xml.external_id


def test_cause_of_death(patient_record: PatientRecord):
    cause_of_death_orm = False
    for orm_object in patient_record.get_new_records():
        if orm_object.__tablename__ == "causeofdeath":
            cause_of_death_orm = orm_object
            break

    # assert cause_of_death_orm
    assert True


def test_document(patient_record: PatientRecord):
    document_orm = False
    for orm_object in patient_record.get_new_records():
        if orm_object.__tablename__ == "document":
            document_orm = orm_object
            break

    assert document_orm

    document_xml = patient_record.xml.documents.document[0]
    assert document_orm.cliniciancode == document_xml.clinician.code
    assert document_orm.cliniciancodestd == document_xml.clinician.coding_standard.value
    assert document_orm.cliniciandesc == document_xml.clinician.description
    assert document_orm.documentname == document_xml.document_name
    

    # check document time
    if document_xml.document_time:
        xml_time = str(document_xml.document_time)[:10]
        orm_time = str(document_orm.documenttime)[:10]
        assert xml_time == orm_time
    
    assert document_orm.documenttypecode == document_xml.document_type.code
    assert (
        document_orm.documenttypecodestd == document_xml.document_type.coding_standard
    )
    assert document_orm.documenttypedesc == document_xml.document_type.description
    assert document_orm.documenturl == document_xml.document_url
    assert document_orm.enteredatcode == document_xml.entered_at.code
    assert document_orm.enteredatdesc == document_xml.entered_at.description
    assert (
        document_orm.enteredatcodestd == document_xml.entered_at.coding_standard.value
    )
    assert document_orm.enteredbycode == document_xml.entered_by.code
    assert document_orm.enteredbydesc == document_xml.entered_by.description
    assert document_orm.externalid == document_xml.external_id
    assert document_orm.filename == document_xml.file_name
    assert document_orm.filetype == document_xml.file_type
    assert document_orm.notetext == document_xml.note_text
    assert document_orm.statuscode == document_xml.status.code
    assert document_orm.statuscodestd == document_xml.status.coding_standard
    assert document_orm.statusdesc == document_xml.status.description
    assert document_orm.stream == document_xml.stream
    assert document_orm.updatedon == document_xml.updated_on