from datetime import datetime
from sqlalchemy.orm import Session
import ukrdc_sqla.ukrdc as orm
from sqlalchemy import select


def validate_demog(session: Session, dob: datetime, pid: str) -> bool:
    """Function to validate a date of birth against a patient record.

    Args:
        session (Session): ukrdc sqlachemy session
        dob (datetime): incoming date of birth.
        pid (str): persistant pid matched to incoming dob

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
        # note to self or other future keyboard tappers, this needs to be
        # thought about more carefully. There may be instances in the future
        # where a patient can have no dob. Also the the whole datetimes as date
        #  should be treated with care.
        raise Exception("something has gone very wrong in the bigger picture")
    else:
        domain_dob = domain_dob[0][0]
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
