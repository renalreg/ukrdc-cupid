from datetime import datetime
from sqlalchemy.orm import Session
import ukrdc_sqla.ukrdc as orm
from sqlalchemy import select, and_
from typing import List

def validate_demog(session: Session, dob:datetime, pid:str):
    """Function to validate a date of birth against a patient record

    Args:
        session (Session): _description_
        dob (datetime): _description_
        pid (str): _description_
    """

    dob_query = select(orm.Patient.birthtime).where(orm.Patient.pid == pid).group_by(orm.Patient.birthtime)
    domain_dob = session.execute(dob_query).fetchall()
    length = len(domain_dob)

    if length == 0: 
        raise Exception("something has gone very wrong in the bigger picture")
    elif length == 1:
        domain_dob = domain_dob[0][0]
        return domain_dob.date() == dob.date()
    else:
        raise Exception("something has gone very wrong in the bigger picture")


def validate_demog_ukrdc(session: Session, dob:datetime, ukrdcid:str):
    """Not sure this is needed 

    Args:
        session (Session): _description_
        dob (datetime): _description_
        pid (str): _description_

    Returns:
        _type_: _description_
    """

    dob_query = select(orm.Patient.birth_time).join(orm.PatientRecord).where(orm.PatientRecord.ukrdcid == ukrdcid).group_by(orm.Patient.birth_time)
    dob_ukrdc = session.execute(dob_query).fetchall()

    return dob in dob_ukrdc
 
    
    
