""" Script to drive the bits of functionality which will end up in the new 
JTrace replacement. The aim here is not to handle any of the merging. Simply 
to load an xml file into a sqla object with all the correct keys.     
"""

from ukrdc_cupid.core.parse.utils import load_xml_from_path
from ukrdc_cupid.core.match.identify import link_patient_number 
from ukrdc_cupid.core.store.models.ukrdc import PatientRecord

from sqlalchemy.orm import sessionmaker
from xsdata.exceptions import ParserError
from sqlalchemy import create_engine

from ukrdc_cupid.core.store.keygen import mint_new_pid
    
#engine = Connection.get_engine_from_file(key="ukrdc_staging")
#session = scoped_session(sessionmaker(engine))
url = "postgresql://postgres:postgres@localhost:5432/dummy_ukrdc"
#engine = create_engine(url, echo = True)
engine = create_engine(url)

ukrdc3_sessionmaker = sessionmaker(bind=engine)
session = ukrdc3_sessionmaker()

# load xml file as python object 
#xml_file = r"Q:\UKRDC\UKRDC Feed Development\RFBAK Leicester\RFBAK_00082_4165311820.xml"
xml_file = r"./xml_examples/UKRDC.xml"
xml_object = load_xml_from_path(xml_file)

if isinstance(xml_object, ParserError):
    print(f"File load failed for the following reason: {xml_object}")
else: 
    # link patient to existing record 
    linked_patients = link_patient_number(session=session, xml=xml_object)

    if len(linked_patients) == 0: 
        # create new pid and load into sqla
        pid = mint_new_pid(session=session)
        patient_record = PatientRecord(xml_object)
        patient_record.map_xml_to_tree()
        patient_record.transform(pid)
        pr_orm = patient_record.assemble_orm_tree()
        print(pr_orm)
        #print(pr_orm.pid)
        for item in pr_orm.lab_orders:
            print(item.pid)
            print(item.id)
            for result in item.result_items:
                print(result)

    elif len(linked_patients) == 1:
        # assign existing pid and ukrdcid 
        patient_record = PatientRecord(xml_object)

        
    else:
        # if multiple matches are returned don't attempt to choose one
        print("Patient cannot be unambigously matched to multiple records")






