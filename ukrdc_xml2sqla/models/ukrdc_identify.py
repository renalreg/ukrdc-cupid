"""Functions to identify items in the dataset already in the ukrdc. 

Returns:
    _type_: _description_
"""

from ukrdc_xml2sqla.models.ukrdc import PatientRecord, PatientNumber
import ukrdc_sqla.ukrdc as orm

import ukrdc_xsdata.ukrdc as xsd_ukrdc
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, select
import pandas as pd


def link_demographics(session: Session, xml: xsd_ukrdc.PatientRecord):
    print("function to link patient on demographic information")


def link_patient_number(session: Session, xml: xsd_ukrdc.PatientRecord):
    """Look up patient from nhs number

    Args:
        session (Session): ukrdc session
        xml (xsd_ukrdc.PatientRecord): ukrdc patient record as xml
    """

    if xml.patient.patient_numbers:
        # patient numbers are the universal source of truth we query these as a first step
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
        #
        demog_match = link_demographics(session, xml)
        return demog_match
