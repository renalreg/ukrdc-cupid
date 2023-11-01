""" Script to drive the bits of functionality which will end up in the new 
JTrace replacement. The aim here is not to handle any of the merging. Simply 
to load an xml file into a sqla object with all the correct keys.     
"""

from ukrdc_cupid.core.parse.utils import load_xml_from_path
from ukrdc_cupid.core.match.identify import link_patient_number 
from ukrdc_cupid.core.store.models.ukrdc import PatientRecord
from ukrdc_cupid.core.store.insert import insert_incoming_data

from sqlalchemy.orm import sessionmaker
from xsdata.exceptions import ParserError
from sqlalchemy import create_engine

from ukrdc_cupid.core.store.keygen import mint_new_pid, mint_new_ukrdcid
    
#engine = Connection.get_engine_from_file(key="ukrdc_staging")
#session = scoped_session(sessionmaker(engine))
url = "postgresql://postgres:postgres@localhost:5432/dummy_ukrdc"
#engine = create_engine(url, echo = True)
engine = create_engine(url)

ukrdc3_sessionmaker = sessionmaker(bind=engine)
session = ukrdc3_sessionmaker()

# load xml file as python object 
#xml_file = r"Q:\UKRDC\UKRDC Feed Development\RFBAK Leicester\RFBAK_00082_4165311820.xml"
xml_file = r"scripts/xml_examples/UKRDC_v4.xml"
xml_object = load_xml_from_path(xml_file)

if isinstance(xml_object, ParserError):
    print(f"File load failed for the following reason: {xml_object}")
else: 
    # link patient to existing record return by order of preference
    linked_patients = link_patient_number(session=session, xml=xml_object)

    if len(linked_patients) == 0: 
        # create new pid and load into sqla
        pid = mint_new_pid(session=session)
        ukrdcid = mint_new_ukrdcid(session = session)

    elif len(linked_patients) > 0 :
        # assign existing pid and ukrdcid 
        pid = linked_patients[0].pid
        ukrdcid = linked_patients[0].ukrdcid

    # map the xml files to ORM objects
    insert_incoming_data(ukrdc_session=session, pid=pid, ukrdcid = ukrdcid, incoming_xml_file=xml_object)