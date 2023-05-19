"""Functions to identify items in the dataset already in the ukrdc. 

Returns:
    _type_: _description_
"""

import ukrdc_sqla.ukrdc as orm

import ukrdc_xsdata.ukrdc as xsd_ukrdc
from sqlalchemy.orm import Session
from sqlalchemy import and_, select
import pandas as pd


def link_demographics(session: Session, xml: xsd_ukrdc.PatientRecord):
    """if no patient numbers are included we match on first name, last name and dob.
    this is assumed to be unique. i.e no two john smiths born on the same day.

    Args:
        session (Session): _description_
        xml (xsd_ukrdc.PatientRecord): _description_
    """
    family_names = [name.family for name in xml.patient.names.name]
    given_names = [name.given for name in xml.patient.names.name]
    patient_demog_query = (
        select(orm.PatientRecord.pid, orm.PatientRecord.ukrdcid)
        .join(orm.Patient, orm.Patient.pid == orm.PatientRecord.pid)
        .join(orm.Name, orm.Name.pid == orm.PatientRecord.pid)
        .filter(orm.Patient.birth_time == xml.patient.birth_time, and_(orm.Name.given.in_(given_names), orm.Name.family.in_(family_names)))
    )

    return pd.read_sql(patient_demog_query, session.bind).drop_duplicates()


def link_patient_number(session: Session, xml: xsd_ukrdc.PatientRecord):
    """Look up patient from nhs number

    Args:
        session (Session): ukrdc session
        xml (xsd_ukrdc.PatientRecord): ukrdc patient record as xml
    """

    if xml.patient.patient_numbers:
        """patient numbers are the universal source of truth we query these as a first step
        if this is incorrect the patient will either be treated as new or matched to the
        wrong patient. This is detectable by checking against demographics data. Do we want
        to add this step in?
        """

        patient_ids = [number.number for number in xml.patient.patient_numbers.patient_number]
        patient_id_types = [number.number_type.value for number in xml.patient.patient_numbers.patient_number]

        patient_number_query = (
            select(orm.PatientRecord.pid, orm.PatientRecord.ukrdcid)
            .join(orm.PatientNumber, orm.PatientNumber.pid == orm.PatientRecord.pid)
            .filter(
                orm.PatientRecord.sendingextract == xml.sending_extract.value,
                orm.PatientRecord.sendingfacility == xml.sending_facility.value,
                and_(orm.PatientNumber.patientid.in_(patient_ids), orm.PatientNumber.numbertype.in_(patient_id_types)),
            )
        )
        return pd.read_sql(patient_number_query, session.bind).drop_duplicates()
    else:
        # try to match using the demographic data
        demog_match = link_demographics(session, xml)
        return demog_match
