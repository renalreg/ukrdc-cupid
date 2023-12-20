"""Functions to identify items in the dataset already in the ukrdc. 

Returns:
    _type_: _description_
"""

import ukrdc_sqla.ukrdc as orm

import ukrdc_xsdata.ukrdc as xsd_ukrdc  # type: ignore
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, tuple_
from ukrdc_cupid.core.audit.validate_matches import validate_demog, validate_demog_ukrdc
from ukrdc_cupid.core.investigate.create_investigation import Investigation

from typing import List, Tuple, Optional


def match_ni(session: Session, patient_info: dict) -> List[Tuple[str, str]]:
    """This secondary matching query in conjunction with the MRN match. It
    should produce matching results to the match_mrn function on the whole.

    Args:
        session (Session): ukrdc database session
        patient_info (dict): dictionary containing the demographic
        information from the patient record.

    Returns:
        List[Tuple[str, str]]: query results containing all the pids and
        ukrdcids matched to the NIs in the patient info.
    """

    # look up pid by trying to match the NI
    pid_query = (
        select(orm.PatientRecord.pid, orm.PatientRecord.ukrdcid)
        .join(orm.PatientNumber, orm.PatientNumber.pid == orm.PatientRecord.pid)
        .where(
            orm.PatientRecord.sendingextract == patient_info["sending_extract"],
            orm.PatientRecord.sendingfacility == patient_info["sending_facility"],
            orm.PatientNumber.numbertype == "NI",
            and_(
                tuple_(orm.PatientNumber.patientid, orm.PatientNumber.organization).in_(
                    patient_info["NI"]
                )
            ),
        )
        .group_by(orm.PatientRecord.pid, orm.PatientRecord.ukrdcid)
    )

    return session.execute(pid_query).fetchall()


def match_mrn(session: Session, patient_info: dict) -> List[Tuple[str, str]]:
    """CUPID will use matching on the MRN as the primary source of truth. All
    This function looks up the MRN with the sendingfacility and sending
    and return all pids and ukrdcids which match.

    Args:
        session (Session): _description_
        patient_info (dict): _description_

    Returns:
        _type_: _description_
    """

    # look up pid by trying to match the MRN
    pid_query = (
        select(orm.PatientRecord.pid, orm.PatientRecord.ukrdcid)
        .join(orm.PatientNumber, orm.PatientNumber.pid == orm.PatientRecord.pid)
        .where(
            orm.PatientRecord.sendingextract == patient_info["sending_extract"],
            orm.PatientRecord.sendingfacility == patient_info["sending_facility"],
            and_(
                orm.PatientNumber.patientid == patient_info["MRN"][0],
                orm.PatientNumber.organization == patient_info["MRN"][1],
                orm.PatientNumber.numbertype == "MRN",
            ),
        )
        .group_by(orm.PatientRecord.pid, orm.PatientRecord.ukrdcid)
    )

    return session.execute(pid_query).fetchall()


def read_patient_metadata(xml: xsd_ukrdc.PatientRecord) -> dict:
    """Function to parse information into a dictionary to be passed round the
    various matching functions.

    Args:
        xml (xsd_ukrdc.PatientRecord): patient record xml parsed with xsdata

    Raises:
        Exception: raised when there is no MRN, this should really never
        happen but it's here for now.

    Returns:
        dict: patient information.
    """

    """

    Args:
        xml (xsd_ukrdc.Patient):
    """
    # we can specify exactly which catagories we want to validate on later
    patient_info = {
        "sending_extract": xml.sending_extract.value,
        "sending_facility": xml.sending_facility.value,
        "birth_time": xml.patient.birth_time.to_datetime(),
        # "gender" : xml.patient.gender,
        # "postcodes" : [address.postcode for address in xml.patient.addresses.address],
        "MRN": None,
        "NI": [],
    }

    # main matching against pid and ukrdc is done using patient numbers
    for number in xml.patient.patient_numbers[0].patient_number:
        if number.number_type.value == "MRN":
            patient_info["MRN"] = [number.number, number.organization.value]

        if number.number_type.value == "NI":
            patient_info["NI"].append([number.number, number.organization.value])

    # MRN is non negotiable for cupid matching
    if not patient_info.get("MRN"):
        raise Exception(
            "placeholder exception...this should really never pass validation"
        )

    return patient_info


def identify_patient_feed(
    session: Session, patient_info: dict
) -> Tuple[Optional[str], Optional[str], Optional[Investigation]]:
    """Identify patient based on patient numbers.

    Args:
        session (Session): SQLAlchemy session
        xml (xsd_ukrdc.PatientRecord): UKRDC patient record as XML
    """

    # match patients on mrn
    matched_patients_mrn = match_mrn(session, patient_info)
    matched_patients_ni = match_ni(session, patient_info)

    # new patient?
    if len(matched_patients_mrn) == 0:
        if len(matched_patients_ni) == 0:
            return None, None, None

    # unambiguously match to single domain patient?
    if len(matched_patients_mrn) > 1:
        investigation = Investigation(matched_patients_mrn, 3)
        return None, None, investigation

    # patient should now be singular
    pid, ukrdcid = matched_patients_mrn[0]

    # validate anonymous patients - bit more thought needed here
    # We probably want to flag if they don't have a domain UID and bypass the
    # validation in that case to overwrite the DOB then future data sends can
    # operate as normal.

    if patient_info["MRN"][1] == "UKRR_UID":
        # validate dob, we use same function but implicitly it is only validating on year of birth
        # I'm assumng these patients wont be sent with NIs
        if validate_demog(session, patient_info["date_of_birth"], pid):
            return pid, ukrdcid, None
        else:
            investigation = Investigation(matched_patients_mrn, 1).create_issue()
            return None, None, investigation

    # check NI and MRN give the same story
    # if the NI's match to anything they should be identical to the MRN
    if matched_patients_mrn != matched_patients_ni and len(matched_patients_ni) != 0:
        investigation = Investigation(
            matched_patients_mrn + matched_patients_ni, 4
        ).create_issue()
        return None, None, investigation

    # check dob
    is_valid = validate_demog(session, patient_info["birth_time"], pid)

    if is_valid:
        return pid, ukrdcid, None
    else:
        investigation = Investigation(matched_patients_mrn, 1).create_issue()
        return None, None, investigation


def match_ukrdc(
    session: Session, patient_ids: List[List[str]]
) -> List[Tuple[str, str]]:

    ukrdc_query = (
        select(orm.PatientRecord.pid, orm.PatientRecord.ukrdcid)
        .join(orm.PatientNumber, orm.PatientNumber.pid == orm.PatientRecord.pid)
        .where(
            tuple_(orm.PatientNumber.patientid, orm.PatientNumber.organization).in_(
                patient_ids
            )
        )
        .group_by(orm.PatientRecord.pid, orm.PatientRecord.ukrdcid)
    )

    return session.execute(ukrdc_query).fetchall()


def identify_across_ukrdc(
    session: Session, patient_info: dict
) -> Tuple[Optional[str], Optional[str], Optional[Investigation]]:
    """Since merging and unmerging patients with ukrdc is easier in the case where a problem arises we just create a new patient and load the file.

    Args:
        session (Session): _description_
        patient_info (dict): _description_
    """

    # search for exact match on incoming id
    ids = patient_info["NI"]

    # certain types of MRN can also be used for matching
    if patient_info["MRN"][1] in ["CHI", "HSC", "NHS"]:
        ids = ids + patient_info

    matched_ids = match_ukrdc(session, ids)
    matched_ukrdcids = []
    for _, ukrdcid in matched_ids:
        if ukrdcid not in matched_ukrdcids:
            matched_ukrdcids.append(ukrdcid)

    # handle results of ukrdc matches
    if len(matched_ukrdcids) == 0:
        return None, None

    elif len(matched_ukrdcids) == 1:
        # verify demgraphics
        _, ukrdcid = matched_ukrdcids[0]
        is_valid = validate_demog_ukrdc(session, patient_info["date_of_birth"], ukrdcid)
        if is_valid:
            return ukrdcid, None
        else:
            investigation = Investigation(
                matched_ids, "Demographic Validation Failure on UKRDCID Match"
            ).create_issue()
            return None, investigation
    else:
        investigation = Investigation(
            matched_ids, "Ambiguous UKRDC Match: matched to multiple persitent UKRDCIDs"
        ).create_issue()
        return None, investigation
