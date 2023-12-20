
from conftest import ukrdc3_session
from sqlalchemy.orm import Session
from ukrdc_cupid.core.store.models.ukrdc import PatientRecord
from ukrdc_cupid.core.store.models.patient import Patient, PatientNumber,Name,ContactDetail,Address,FamilyDoctor
from ukrdc_cupid.core.parse.utils import load_xml_from_path
from datetime import datetime
import ukrdc_xsdata.ukrdc as xsd # type: ignore
import glob
import os
import pytest


""" Test 1 - Patient and Demographics Testing
Files to load:
test_1a.xml
test_1b.xml 
"""

@pytest.fixture(scope="function")
def test_ukrdc_session()->Session:
    return ukrdc3_session
 
def test_patient_record(test_ukrdc_session:Session)->None:
    xml_test_1a = load_xml_from_path(os.path.join("tests","xml_files","store_tests","test_1a.xml"))
    patient_record = PatientRecord(xml_test_1a)
    patient_record.map_to_database("test_pid", "test_ukrdcid", test_ukrdc_session)
    
    # check attributes have been mapped as expected
    assert patient_record.orm_object.pid == "test_pid"
    assert patient_record.orm_object.ukrdcid == "test_ukrdcid"
    assert patient_record.orm_object.localpatientid == "AAA111B"
    assert patient_record.orm_object.sendingfacility == "RFCAT"
    assert patient_record.orm_object.sendingextract == "UKRDC"

    # check patient mapped
    assert isinstance(patient_record.mapped_classes[0],Patient)
    assert len(patient_record.mapped_classes) == 1

def test_patient(test_ukrdc_session:Session)->None:
    xml_test_1a = load_xml_from_path(os.path.join("tests","xml_files","store_tests","test_1a.xml"))
    patient_xml = xml_test_1a.patient
    patient = Patient(patient_xml)
    patient.map_to_database(test_ukrdc_session,"test_pid", 0)
    patient.map_xml_to_orm(test_ukrdc_session)

    # check attributes of orm objects 
    assert patient.orm_object.birthtime == datetime(1969,6,9)
    assert patient.orm_object.countryofbirth == "MOO"
    assert patient.orm_object.death == True
    assert patient.orm_object.deathtime == datetime(1984,6,9)
    assert patient.orm_object.gender == "1"

    # check correct child classes have been created
    child_classes = [
        PatientNumber, 
        PatientNumber, 
        Name, 
        ContactDetail, 
        Address, 
        FamilyDoctor
    ]
#    for actual, expected in zip(child_classes, patient.mapped_classes):
#        assert isinstance(expected, actual)

#test_patient(test_ukrdc_session())
#print(":)")

