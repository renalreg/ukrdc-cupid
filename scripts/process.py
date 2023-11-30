""" Script to drive the bits of functionality which will end up in the new 
JTrace replacement. The aim here is not to handle any of the merging. Simply 
to load an xml file into a sqla object with all the correct keys.     
"""

import glob
import os

from ukrdc_cupid.core.parse.utils import load_xml_from_path
from ukrdc_cupid.core.match.identify import identify_patient_feed, read_patient_metadata, identify_across_ukrdc
from ukrdc_cupid.core.store.insert import insert_incoming_data, insert_into_sherlock

from sqlalchemy.orm import sessionmaker
from xsdata.exceptions import ParserError
from sqlalchemy import create_engine

from ukrdc_cupid.core.store.keygen import mint_new_pid, mint_new_ukrdcid


def process_file(xml_object):
    if isinstance(xml_object, ParserError):
        raise f"File load failed for the following reason: {xml_object}"
    
    # Attempt to identify patient on same feed
    patient_info = read_patient_metadata(xml_object)
    pid, ukrdcid, investigation = identify_patient_feed(session=session, patient_info=patient_info)

    # Investigations cause file to be diverted
    if investigation:
        insert_into_sherlock(investigation, xml_object)
        return

    # After this point files will be inserted into ukrdc        
    # Mint a pid if we don't have one
    if not pid: 
        pid = mint_new_pid(session=session)
        is_new = True # need to revisit this
    else:
        is_new = False

    # Attempt to identify patient across the ukrdc
    if not ukrdcid:
        ukrdcid, investigation = identify_across_ukrdc(session, patient_info, pid)

    # mint new ukrdcid    
    if not ukrdcid:
        ukrdcid = mint_new_ukrdcid(session=session)

    # insert data
    new, dirty, unchanged = insert_incoming_data(
        ukrdc_session=session, 
        pid=pid, 
        ukrdcid=ukrdcid, 
        incoming_xml_file=xml_object,
        is_new = is_new,  
        debug = True
    )

    # insert investigations
    if investigation:
        insert_into_sherlock(investigation)


url = "postgresql://postgres:postgres@localhost:5432/dummy_ukrdc"
engine = create_engine(url)

ukrdc3_sessionmaker = sessionmaker(bind=engine, expire_on_commit=True)
session = ukrdc3_sessionmaker()


# Specify the directory where your XML files are located
xml_directory = ".xml_to_load"

# grab files to load from directory
xml_files = glob.glob(os.path.join(xml_directory, "*.xml"))


for xml_file in xml_files:
    xml_object = load_xml_from_path(xml_file)
    process_file(xml_object)

