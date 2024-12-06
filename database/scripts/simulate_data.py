"""
Script to lift files from the UKRDC to simulate data dump. We only need the
bits to match the schema converter archive. =
"""

from sqlalchemy.orm import sessionmaker, with_polymorphic
from sqlalchemy import create_engine, text
from dotenv import dotenv_values
from ukrdc_cupid.core.match.identify import match_mrn, read_patient_metadata
from ukrdc_cupid.core.parse.utils import load_xml_from_path
from ukrdc_sqla.ukrdc import PatientRecord
from sqlalchemy import select
from sqlalchemy.orm import class_mapper

from pathlib import Path


# Load environment variables
ENV = dotenv_values(".env.database")
CENTRES = [
    "RK7CC"
]

# Database URLs
ukrdc_live_url = ENV["UKRDC_URL"]
test_db_url = ENV["CUPID_URL"]

# Create database engines
ukrdc_live_engine = create_engine(ukrdc_live_url)
cupid_test_engine = create_engine(test_db_url)

# Create session factories
LiveSession = sessionmaker(bind=ukrdc_live_engine, autoflush=False, autocommit=False)
CupidSession = sessionmaker(bind=cupid_test_engine)

# Start sessions for both databases
with LiveSession() as live_session:
    with CupidSession() as cupid_session:
        patient_record_hierarchy = with_polymorphic(
            PatientRecord, "*"
        )

        # Query the hierarchy and get all related polymorphic objects
        centre_prs = (
            live_session.query(patient_record_hierarchy)
            #live_session.query(PatientRecord)
            .filter(PatientRecord.sendingfacility.in_(CENTRES))
            .all()  # This returns the whole hierarchy
        )
        
        total_to_transfer = len(centre_prs)
        i = 0 
        for pr in centre_prs:  
                children = []
                i+=1 
                print(f"transfering patient {i} / {total_to_transfer}")
                patient = pr.patient
                children.append(patient)
                #allergies = [allergy for allergy in pr.allergies]
                children += patient.numbers
                children += patient.names
                children += patient.contact_details
                children += patient.addresses
                children.append(patient.familydoctor)
                children += pr.treatments
                children += pr.lab_orders  # Add lab orders
                children += pr.result_items  # Add result items
                """
                children += pr.observations  # Add observations
                children += pr.social_histories  # Add social histories
                children += pr.family_histories  # Add family histories
                children += pr.allergies  # Add allergies
                children += pr.diagnoses  # Add diagnoses
                children += pr.cause_of_death  # Add cause of death
                children += pr.renaldiagnoses  # Add renal diagnoses
                children += pr.medications  # Add medications
                children += pr.dialysis_sessions  # Add dialysis sessions
                children += pr.vascular_accesses  # Add vascular accesses
                children += pr.procedures  # Add procedures    
                children += pr.encounters  # Add encounters
                children += pr.transplantlists  # Add transplant lists
                children += pr.program_memberships  # Add program memberships
                children += pr.transplants  # Add transplants
                children += pr.opt_outs  # Add opt-outs
                children += pr.clinical_relationships  # Add clinical relationships
                children += pr.surveys  # Add surveys
                """

                # Detach the patient object from the live session
                live_session.expunge(pr)
                cupid_session.execute(text(f"SET search_path TO extract"))
                cupid_session.merge(pr)
                for child in children:
                    if child is not None:
                        cupid_session.merge(child) 
            
                cupid_session.commit()

