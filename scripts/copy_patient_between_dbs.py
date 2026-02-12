"""
Simple script to copy patient records between a source and a destination copy
of the ukrdc.
"""

from sqlalchemy.orm import sessionmaker, with_polymorphic, Session
from sqlalchemy import create_engine
from dotenv import dotenv_values
from ukrdc_sqla.ukrdc import PatientRecord

ENV = dotenv_values(".env.scripts")

# Database URLs
source_url = ENV["SOURCE_DB_URL"]
destination_url = ENV["DEST_DB_URL"]

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

def copy_patient_by_ukrdcid(source_session:Session, destination_session:Session, ukrdcid):
    """
    Copy a patient record from the source session to the destination session.
    """
    patient_record_hierarchy = with_polymorphic(
        PatientRecord, "*"
    )

    # Query the hierarchy and get all related polymorphic objects
    patients = (
        source_session.query(patient_record_hierarchy)
        .filter(PatientRecord.ukrdcid == ukrdcid)
        .all()  # This returns the whole hierarchy
    )

    children = []
    for pr in patients:
        if destination_session.get(PatientRecord, pr.pid):
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
        children += pr.lab_orders  # Add lab orders
        children += pr.result_items  # Add result items
        children += pr.observations  # Add observations
        children += pr.social_histories  # Add social histories
        children += pr.family_histories  # Add family histories
        children += pr.allergies  # Add allergies
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
        source_session.expunge(pr)
        destination_session.merge(pr)
        for child in children:
            if child is not None:
                destination_session.merge(child) 
        destination_session.commit()

def get_ukrdcid_from_facility(source_session:Session,facility:str):
    return [
        item[0] for item in 
        source_session.query(PatientRecord.ukrdcid).filter(PatientRecord.sendingfacility == facility).all()
    ]


if __name__ == "__main__":
    facility = "RNJ00"
    ukrdcids = ['100208388']
    source_db_engine = create_engine(ENV["SOURCE_DB_URL"])
    destination_db_engine = create_engine(ENV["DEST_DB_URL"])
    source_session = sessionmaker(bind=source_db_engine)
    destination_session = sessionmaker(bind=destination_db_engine)
    with source_session() as source_session:
        # if facility is supplied overwrite ukrdcids
        if facility:
            ukrdcids = get_ukrdcid_from_facility(source_session,facility)
        
        with destination_session() as destination_session:
            for ukrdcid in ukrdcids[:100]:
                copy_patient_by_ukrdcid(source_session, destination_session, ukrdcid)
