"""Functions to identify items in the dataset already in the ukrdc. 

Returns:
    _type_: _description_
"""

import ukrdc_sqla.ukrdc as orm

import ukrdc_xsdata.ukrdc as xsd_ukrdc  # type: ignore
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from sqlalchemy import and_, tuple_, select
from datetime import datetime


def validate_dob(ukrdcid: Optional[str], incoming_dob: datetime):
    """Simple sanity check validation of ukrdcid

    Args:
        pid (Optional[str]): _description_
        ukrdcid (Optional[str]): _description_
    """
    return True


def link_patient_number(
    session: Session,
    sending_facility: str,
    sending_extract: str,
    patient_id_numbertype_pairs: List[Tuple[str, str]],
):
    """Look up patient from patient IDs and organization types.

    Args:
        session (Session): ukrdc session
        sending_facility (str): The sending facility
        sending_extract (str): The sending extract
        patient_id_numbertype_pairs (List[Tuple[str, str]]): List of tuples representing pairs of (patientid, numbertype)
    """

    patient_number_query = (
        select(orm.PatientRecord.pid, orm.PatientRecord.ukrdcid)
        .join(orm.PatientNumber, orm.PatientNumber.pid == orm.PatientRecord.pid)
        .where(
            orm.PatientRecord.sendingextract == sending_extract,
            orm.PatientRecord.sendingfacility == sending_facility,
            and_(
                tuple_(orm.PatientNumber.patientid, orm.PatientNumber.organization).in_(
                    patient_id_numbertype_pairs
                ),
            ),
        )
        .group_by(orm.PatientRecord.pid, orm.PatientRecord.ukrdcid)
    )

    # linked_patients = [row for row in session.execute(patient_number_query)]
    linked_patients = session.execute(patient_number_query).fetchall()
    return linked_patients


def link_ukrdcid(
    session: Session, patient_id_numbertype_pairs: List[Tuple[str, str]]
) -> Optional[str]:
    """This function operate similar to the function above but will link patients from different feeds.

    Args:
        session (Session): _description_
        patient_ids (List[str]): _description_
        patient_id_orgs (List[str]): _description_
    """
    patient_number_query = (
        select(orm.PatientRecord.pid, orm.PatientRecord.ukrdcid)
        .join(orm.PatientNumber, orm.PatientNumber.pid == orm.PatientRecord.pid)
        .where(
            tuple_(orm.PatientNumber.patientid, orm.PatientNumber.organization).in_(
                patient_id_numbertype_pairs
            ),
        )
        .group_by(orm.PatientRecord.pid, orm.PatientRecord.ukrdcid)
    )

    linked_patients = session.execute(patient_number_query).fetchall()
    return linked_patients


def identify_patient(session: Session, xml: xsd_ukrdc.PatientRecord):
    """Identify patient based on patient numbers.

    Args:
        session (Session): SQLAlchemy session
        xml (xsd_ukrdc.PatientRecord): UKRDC patient record as XML
    """

    if xml.patient.patient_numbers:
        patient_id_numbertype_pairs = [
            (number.number, number.organization.value)
            for number in xml.patient.patient_numbers[0].patient_number
        ]
        sending_extract = xml.sending_extract.value
        sending_facility = xml.sending_facility.value

    else:
        raise Exception("Placeholder exception")

    # First, we try to unambiguously look up the patient
    linked_patients = link_patient_number(
        session, sending_facility, sending_extract, patient_id_numbertype_pairs
    )

    if len(linked_patients) == 0:
        # No linked patients means several possibilities
        # 1) Patient is new to unit but not new to us.
        # 2) Patient does have pid but cannot be identified due to data issues
        # 3) Patient is new to us and new to the unit.

        return None, None

    elif len(linked_patients) == 1:
        # Return the pid and the ukrdcid if match is unambigous
        # it shouldn't be possible for the ukrdcid to be null
        # we also check dob matches

        return linked_patients[0]
    else:
        # Combination of dob, sending_facility, sending extract and patient number should be unique.
        # if it is not we shouldn't assume any particular patient is the right one and should flag
        # a data quality issue.
        return None, None
