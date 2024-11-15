"""Functions to identify items in the dataset already in the ukrdc. 

Returns:
    _type_: _description_
"""

import ukrdc_sqla.ukrdc as orm
import ukrdc_xsdata.ukrdc as xsd_ukrdc  # type: ignore

from sqlalchemy.orm import Session
from sqlalchemy import select, and_, tuple_
from ukrdc_cupid.core.audit.validate_matches import (
    validate_demog,
    validate_demog_ukrdc,
    validate_NI_mismatch,
)
from ukrdc_cupid.core.investigate.models import Issue, PatientID, LinkPatientToIssue
from ukrdc_cupid.core.investigate.create_investigation import Investigation

from typing import List, Any
from nhs_number.validate import is_valid


def match_ni(session: Session, patient_info: dict) -> Any:
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


def match_mrn(session: Session, patient_info: dict) -> Any:
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
        "channel": xml.sending_facility.channel_name,
        "sending_time": xml.sending_facility.time,
        "schema_version": xml.sending_facility.schema_version,
        "birth_time": xml.patient.birth_time.to_datetime(),
        # "gender" : xml.patient.gender,
        # "postcodes" : [address.postcode for address in xml.patient.addresses.address],
        "MRN": None,
        "NI": [],
    }

    # main matching against pid and ukrdc is done using patient numbers.
    # validate these numbers where possible.
    for number in xml.patient.patient_numbers.patient_number:
        if number.number_type.value == "MRN":
            patient_info["MRN"] = [number.number, number.organization.value]

        if number.number_type.value == "NI":
            patient_info["NI"].append([number.number, number.organization.value])

        if number.organization.value in ("NHS", "HSC", "CHI"):
            if not is_valid(number.number):
                raise Exception("placeholder exception...nhs number invalid")

    # MRN is non negotiable for cupid matching
    if not patient_info.get("MRN"):
        raise Exception(
            "placeholder exception...this should really never pass validation"
        )

    return patient_info


def match_pid(ukrdc_session: Session, patient_info: dict) -> Any:
    """See documentation for overview of how this is working:
    https://renalregistry.atlassian.net/wiki/x/BQAfkw

    The patient info is matched (or not) with the MRN. It then goes through
    as series of steps to confirm or otherwise the match.

    In reality the introduction of the UKRR_UID has made in the defacto key for
    and matching.

    Args:
        ukrdc_session (Session): _description_
        patient_info (dict): _description_

    Returns:
        Any: _description_
    """

    # match patients on mrn and NI
    matched_patients_mrn = match_mrn(ukrdc_session, patient_info)
    matched_patients_ni = match_ni(ukrdc_session, patient_info)
    matched_mrn_no = len(matched_patients_mrn)
    matched_ni_no = len(matched_patients_ni)

    # new patient?
    if matched_mrn_no == 0:
        if matched_ni_no == 0:
            return None, None, None
        else:
            return None, None, Investigation(ukrdc_session, matched_patients_ni, 2)

    # set the pid based on the matched mrn
    elif matched_mrn_no == 1:
        pid, ukrdcid = matched_patients_mrn[0]

    # return investigation if multiple matches have been found
    else:
        return None, None, Investigation(ukrdc_session, matched_patients_mrn, 3)

    # detect if anonymized record and change goalposts slightly
    # we could also consider blanking the ukrdc id here if its the first
    # time the patient has been seen in anonymized form this would mean
    # a new ukrdc id would get minted unlinking it from other patients
    # alternatively this could easily be done by a separate process maybe
    # the one that issue the UKRR_UID in the first place.
    is_anon = patient_info["MRN"][1] == "UKRR_UID"
    is_valid = validate_demog(
        ukrdc_session, patient_info["birth_time"], pid, is_anon=is_anon
    )

    if not is_valid:
        return None, None, Investigation(ukrdc_session, matched_patients_mrn, 1)

    # anonymized have no further checks carried out
    if is_anon:
        return pid, ukrdcid, None

    # records with no NI matches cannot be validated
    if matched_ni_no == 0:
        return None, None, Investigation(ukrdc_session, matched_patients_mrn, 2)

    # check ni and mrn matches tell the same story
    is_consistent = matched_patients_mrn == matched_patients_ni
    if is_consistent:
        return pid, ukrdcid, None

    else:
        mismatch_failed = validate_NI_mismatch(pid)
        if mismatch_failed == 0:
            patients = matched_patients_mrn + [
                patient
                for patient in matched_patients_ni
                if patient not in matched_patients_mrn
            ]
            return (
                None,
                None,
                Investigation(ukrdc_session, patients, 4),
            )
        else:
            print("Placeholder for logic where the mismatch is allowed")
            return pid, ukrdcid, None


def identify_patient_feed(ukrdc_session: Session, patient_info: dict) -> Any:
    """
    Function matches xml file to patient feed and checks for open
    investigations against that patient. If a successful match is made
    and it is verified that no investigations are blocking the file it will
    return the pid and ukrdcid of the patient. Otherwise an investigation is
    returned.

    Args:
        ukrdc_session (Session): _description_
        patient_info (dict): _description_

    Returns:
        Any: _description_
    """
    pid, ukrdcid, investigation = match_pid(ukrdc_session, patient_info)

    # if pid has been found but there were previously problems we generate a
    # new investigation
    if pid is not None:
        query = (
            select(PatientID)
            .join(LinkPatientToIssue, PatientID.id == LinkPatientToIssue.c.patient_id)
            .join(Issue, Issue.id == LinkPatientToIssue.c.issue_id)
            .where(
                and_(
                    PatientID.pid == pid,
                    Issue.is_blocking is True,
                    Issue.is_resolved is False,
                )
            )
            .limit(1)
        )
        open_investigation = ukrdc_session.execute(query).scalar_one_or_none()

        if open_investigation is not None:
            investigation = Investigation(ukrdc_session, [(pid, ukrdcid)], 7)
            pid = None
            ukrdcid = None

    return pid, ukrdcid, investigation


'''
def identify_patient_feed(ukrdc_session: Session, patient_info: dict) -> Any:
    """Identify patient based on patient numbers. It uses a combination of
    three different bits of information. The NI, the MRN and the demographics
    (DOB). In all instances if the three bits of information don't match the
    file will not load and an investigation will be raised. The MRN can be
    changed as long as it doesn't match to a different patient feed to the
    NI.

    Args:
        session (Session): SQLAlchemy session
        xml (xsd_ukrdc.PatientRecord): UKRDC patient record as XML
    """

    # match patients on mrn and NI
    matched_patients_mrn = match_mrn(ukrdc_session, patient_info)
    matched_patients_ni = match_ni(ukrdc_session, patient_info)

    # new patient?
    if len(matched_patients_ni) == 0:
        # when no match is found with ni we have a go with MRN
        # if this can be validated against the dob
        if len(matched_patients_mrn) == 0:
            return None, None, None
        elif len(matched_patients_mrn) == 1:
            # we could remove this step if we decide it shouldn't be possible
            # to overwrite NI
            pid, ukrdcid = matched_patients_mrn[0]

    elif len(matched_patients_ni) == 1:
        pid, ukrdcid = matched_patients_ni[0]

    # check MRN look up returns a single patient
    if len(matched_patients_mrn) > 1:
        investigation = Investigation(ukrdc_session, matched_patients_mrn, 3)
        investigation.create_issue()
        # information to store about issue

        return None, None, investigation

    # validate anonymous patients - bit more thought needed here
    # We probably want to flag if they don't have a domain UID and bypass the
    # validation in that case to overwrite the DOB then future data sends can
    # operate as normal.

    if patient_info["MRN"][1] == "UKRR_UID":
        # validate dob, we use same function but implicitly it is only validating on year of birth
        # I'm assuming these patients won't be sent with NIs
        if validate_demog(ukrdc_session, patient_info["date_of_birth"], pid):
            return pid, ukrdcid, None
        else:
            investigation = Investigation(
                ukrdc_session, matched_patients_mrn, 1
            )
            investigation.create_issue()
            return None, None, investigation

    # check NI and MRN give the same story
    # if the NI's match to anything they should be identical to the MRN
    if matched_patients_mrn != matched_patients_ni and len(matched_patients_ni) != 0:
        investigation = Investigation(
            ukrdc_session, matched_patients_mrn + matched_patients_ni, 4
        )
        investigation.create_issue()
        return None, None, investigation

    # check dob
    is_valid = validate_demog(ukrdc_session, patient_info["birth_time"], pid)

    if is_valid:
        return pid, ukrdcid, None
    else:
        investigation = Investigation(
            ukrdc_session, matched_patients_mrn, 1
        )
        investigation.create_issue()
        return None, None, investigation
'''


def match_ukrdc(session: Session, patient_ids: List[List[str]]) -> Any:

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


def identify_across_ukrdc(ukrdc_session: Session, patient_info: dict) -> Any:
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

    matched_ids = match_ukrdc(ukrdc_session, ids)
    matched_ukrdcids = []
    for _, ukrdcid in matched_ids:
        if ukrdcid not in matched_ukrdcids:
            matched_ukrdcids.append(ukrdcid)

    # handle results of ukrdc matches
    if len(matched_ukrdcids) == 0:
        return None, None

    elif len(matched_ukrdcids) == 1:
        # verify dem0graphics
        ukrdcid = matched_ukrdcids[0]
        is_valid = validate_demog_ukrdc(
            ukrdc_session, patient_info["birth_time"], ukrdcid
        )
        if is_valid:
            return ukrdcid, None
        else:
            investigation = Investigation(
                ukrdc_session, matched_ids, 5, is_blocking=False
            )
            return None, investigation
    else:
        investigation = Investigation(ukrdc_session, matched_ids, 6, is_blocking=False)
        return None, investigation
