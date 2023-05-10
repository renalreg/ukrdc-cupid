""" Script to drive the bits of functionality which will end up in the new 
JTrace replacement. The aim here is not to handle any of the merging. Simply 
to load an xml file into a sqla object with all the correct keys.     
"""


import glob

from ukrdc_xml2sqla.utils import load_xml_from_path, mint_new_pid
from ukrdc_xml2sqla.models.ukrdc_identify import link_patient_number 
from ukrdc_xml2sqla.models.ukrdc import PatientRecord
from sqlalchemy.orm import sessionmaker, scoped_session
from ukrdc.database import Connection
from xsdata.exceptions import ParserError

    
engine = Connection.get_engine_from_file(key="ukrdc_staging")
session = scoped_session(sessionmaker(engine))


# load xml file as python object 
#xml_file = r"Q:\UKRDC\UKRDC Feed Development\RFBAK Leicester\RFBAK_00082_4165311820.xml"
xml_file = r"xml_examples\UKRDC.xml"
xml_object = load_xml_from_path(xml_file)

if isinstance(xml_object, ParserError):
    print(f"File load failed for the following reason: {xml_object}")
else: 
    # link patient to existing record 
    linked_patients = link_patient_number(session=session, xml=xml_object)

    if len(linked_patients) == 0: 
        # create new pid and load into sqla
        pid = mint_new_pid(session=session, patient=xml_object)
        patient_record = PatientRecord(xml=xml_object, pid = pid).to_orm()

    elif len(linked_patients) == 1:
        # assign existing pid and ukrdcid 
        patient_record = PatientRecord(xml=xml_object, pid = linked_patients.pid.iloc[0]).to_orm()
        patient_record.ukrdcid = linked_patients.ukrdcid.iloc[0]
    else:
        print("Patient cannot be unambigously matched to multiple records")






