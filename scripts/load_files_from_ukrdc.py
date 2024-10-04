"""
Script to lift files from the UKRDC staging, detach, and insert them into the test database.
"""

"""
Script to lift files from the UKRDC staging, detach, and insert them into the test database,
using polymorphism to download the whole hierarchy.
"""

from sqlalchemy.orm import sessionmaker, with_polymorphic
from sqlalchemy import create_engine
from dotenv import dotenv_values
from ukrdc_cupid.core.match.identify import match_mrn, read_patient_metadata
from ukrdc_cupid.core.parse.utils import load_xml_from_path
from ukrdc_sqla.ukrdc import PatientRecord

from pathlib import Path

# Load environment variables
ENV = dotenv_values(".env.scripts")

# Database URLs
ukrdc_live_url = ENV["UKRDC_URL"]
test_db_url = ENV["CUPID_URL"]

# XML file folder
xml_folder = Path(".xml_decrypted")
xml_files = [file for file in xml_folder.glob("*.xml")]

# Create database engines
ukrdc_live_engine = create_engine(ukrdc_live_url)
cupid_test_engine = create_engine(test_db_url)

# Create session factories
LiveSession = sessionmaker(bind=ukrdc_live_engine)
CupidSession = sessionmaker(bind=cupid_test_engine)

# Start sessions for both databases
with LiveSession() as live_session:
    with CupidSession() as cupid_session:
        for xml_file in xml_files:
            pid = None
            try:
                # Load XML and extract patient information
                xml = load_xml_from_path(xml_file)
                patient_info = read_patient_metadata(xml)
                
                # Match MRN and get the patient info from the live session
                output = match_mrn(live_session, patient_info)
                if output:
                    pid, ukrdcid = output[0]
                    
                    
                    if ukrdcid:
                        print(f"Transferring patient with ukrdcid {ukrdcid}")
                        # Use polymorphic query to fetch the entire hierarchy for PatientRecord
                        patient_record_hierarchy = with_polymorphic(
                            PatientRecord, "*"
                        )

                        # Query the hierarchy and get all related polymorphic objects
                        patients = (
                            live_session.query(patient_record_hierarchy)
                            #live_session.query(PatientRecord)
                            .filter(PatientRecord.ukrdcid == ukrdcid)
                            .all()  # This returns the whole hierarchy
                        )

                        for pr in patients:
                            patient = pr.patient
                            patient_numbers = [number for number in patient.numbers]

                            # Detach the patient object from the live session
                            live_session.expunge(pr)
                            cupid_session.merge(pr)       

                            for number in patient_numbers:
                                live_session.expunge(number)
                                cupid_session.merge(number)

                            cupid_session.merge(patient)

            
                            cupid_session.commit()
            except Exception as e:
                print(e)
                print(f"{pid} could not be transfered")

