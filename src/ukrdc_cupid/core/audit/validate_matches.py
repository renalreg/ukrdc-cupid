from datetime import datetime
from sqlalchemy.orm import Session
import ukrdc_sqla.ukrdc as orm
from sqlalchemy import select


def validate_demog(
    session: Session, dob: datetime, pid: str, is_anon: bool = False
) -> bool:
    """Function to validate a date of birth against a patient record.

    Args:
        session (Session): ukrdc sqlachemy session
        dob (datetime): incoming date of birth.
        pid (str): persistent pid matched to incoming dob

    Raises:
        Exception: there should be only 1 (or possibly None) dob per patient
        record. This exception needs fleshing see comment.

    Returns:
        bool: whether dob matches what we think it should
    """

    dob_query = select(orm.Patient.birthtime).where(orm.Patient.pid == pid)
    domain_dob = session.execute(dob_query).fetchall()
    length = len(domain_dob)

    if length != 1:
        # To be expanded when properly thought through
        raise Exception("validate_demog is broken")
    else:
        domain_dob = domain_dob[0][0]
        if is_anon:
            # anonomised patients only get validated on year this allows a
            # a record to be overridden
            return domain_dob.date().year == domain_dob.date().year
        else:
            return domain_dob.date() == dob.date()  # type:ignore


def validate_demog_ukrdc(session: Session, dob: datetime, ukrdcid: str) -> bool:
    """Currently I (PM) think its a bit over the top validating the
    demographics when you match ukrdcid but will leave it for now.

    Args:
        session (Session): sqlalchemy session for ukrdc database
        dob (datetime):
        pid (str): _description_

    Returns:
        _type_: _description_
    """

    dob_query = (
        select(orm.Patient.birth_time)
        .join(orm.PatientRecord)
        .where(orm.PatientRecord.ukrdcid == ukrdcid)
        .group_by(orm.Patient.birth_time)
    )
    dob_ukrdc = session.execute(dob_query).fetchall()

    return dob in dob_ukrdc


def validate_NI_mismatch(pid: str):
    """This function is a placeholder the idea is that there might be specific
    circumstances where we allow a NI to be overwritten. For example if you
    were to overwrite a chi number with a nhs number or possibly even correct
    an NHS number.
    """
    # some sql to look up the patient numbers against the pid
    # some logic to deduce if the change is one we expect
    # we then assign a classification
    NI_mismatch_type = 1

    # or maybe anther based on some other criterion
    # e.g organisation = NHS_corrected
    NI_mismatch_type = 2

    # otherwise we default to a validation failure
    NI_mismatch_type = 0

    return NI_mismatch_type
