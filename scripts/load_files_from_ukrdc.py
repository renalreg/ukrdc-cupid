"""
Script to lift files from the UKRDC staging, detach, and insert them into the test database.
"""

"""
Script to lift files from the UKRDC staging, detach, and insert them into the test database,
using polymorphism to download the whole hierarchy.
"""

GLOBAL_LAZY = "selectin"

from sqlalchemy.orm import sessionmaker, with_polymorphic
from sqlalchemy import create_engine
from dotenv import dotenv_values
from ukrdc_cupid.core.match.identify import match_mrn, read_patient_metadata
from ukrdc_cupid.core.parse.utils import load_xml_from_path
from ukrdc_sqla.ukrdc import PatientRecord

from pathlib import Path

ATTR_PATHS = [
    "patient",               # Primary patient object
    "patient.numbers",        # Patient numbers
    "patient.names",          # Patient names
    "patient.contact_details",# Patient contact details
    "patient.addresses",      # Patient addresses
    "patient.familydoctor",   # Family doctor
    "treatments",             # Treatments
    "lab_orders",             # Lab orders
    "result_items",           # Result items
    "observations",           # Observations
    "social_histories",       # Social histories
    "family_histories",       # Family histories
    "allergies",              # Allergies
    #"diagnoses",             # Diagnoses (commented out if not needed)
    #"cause_of_death",        # Cause of death (commented out if not needed)
    #"renaldiagnoses",        # Renal diagnoses (commented out if not needed)
    "medications",            # Medications
    "dialysis_sessions",      # Dialysis sessions
    "vascular_accesses",      # Vascular accesses
    "procedures",             # Procedures
    #"documents",             # Documents (commented out if not needed)
    "encounters",             # Encounters
    "transplantlists",        # Transplant lists
    "program_memberships",    # Program memberships
    "transplants",            # Transplants
    "opt_outs",               # Opt-outs
    "clinical_relationships", # Clinical relationships
    "surveys",                # Surveys
]

# Load environment variables
ENV = dotenv_values(".env.scripts")
CENTRES = [
    "RH8"
]

# Database URLs
ukrdc_live_url = ENV["UKRDC_URL"]
test_db_url = ENV["CUPID_URL"]

# XML file folder
xml_folder = Path(".xml_decrypted")
xml_files = [file for file in xml_folder.glob("*.xml") if file.stem.split("_")[0] in CENTRES]

# Create database engines
ukrdc_live_engine = create_engine(ukrdc_live_url)
cupid_test_engine = create_engine(test_db_url)

# Create session factories
LiveSession = sessionmaker(bind=ukrdc_live_engine, autoflush=False, autocommit=False)
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
                        children = []
                        for pr in patients:
                            if cupid_session.get(PatientRecord, pr.pid):
                                continue


                            patient = pr.patient
                            children.append(patient)
                            #allergies = [allergy for allergy in pr.allergies]
                            children += patient.numbers
                            children += patient.names
                            children += patient.contact_details
                            children += patient.addresses
                            children.append(patient.familydoctor)


                            children += pr.treatments
                            #children += [number for number in patient.numbers]
                            #children += [treatment for treatment in pr.treatments]
                            children += pr.lab_orders  # Add lab orders
                            children += pr.result_items  # Add result items
                            children += pr.observations  # Add observations
                            children += pr.social_histories  # Add social histories
                            children += pr.family_histories  # Add family histories
                            children += pr.allergies  # Add allergies
                            #children += pr.diagnoses  # Add diagnoses
                            #children += pr.cause_of_death  # Add cause of death
                            #children += pr.renaldiagnoses  # Add renal diagnoses
                            children += pr.medications  # Add medications
                            children += pr.dialysis_sessions  # Add dialysis sessions
                            children += pr.vascular_accesses  # Add vascular accesses
                            children += pr.procedures  # Add procedures



                            #children += pr.documents  # Add documents
                            children += pr.encounters  # Add encounters
                            children += pr.transplantlists  # Add transplant lists
                            children += pr.program_memberships  # Add program memberships
                            children += pr.transplants  # Add transplants
                            children += pr.opt_outs  # Add opt-outs
                            children += pr.clinical_relationships  # Add clinical relationships
                            children += pr.surveys  # Add surveys

                            # Detach the patient object from the live session
                            live_session.expunge(pr)
                            cupid_session.merge(pr)
                            for child in children:
                                if child is not None:
                                    cupid_session.merge(child) 


            
                            cupid_session.commit()
            except Exception as e:
                print(e)
                print(f"{pid} could not be transfered")

