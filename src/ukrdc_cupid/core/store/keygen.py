"""
Primary keys for the records contained within the ukrdc. Hopefully we simplify
this at some point in the future. Currently it's designed to replicate the data
repository however I think a lot of that was hacked together to work with the
limitations of jtrace. 
"""

import random
import string

from sqlalchemy.orm import Session
from sqlalchemy import Sequence
import ukrdc_sqla.ukrdc as sqla
import ukrdc_xsdata.ukrdc.lab_orders as xsd_lab_orders  # type:ignore
import ukrdc_xsdata.ukrdc.dialysis_sessions as xsd_dialysis_sessions

from typing import Optional

KEY_SEPERATOR = ":"


def mint_new_pid(session: Session) -> str:
    """
    Function to mint new pid. This sequence doesn't currently exist in the ukrdc, create by running script make_pid_generation_sequence.py
    """

    new_pid = str(session.execute(Sequence("generate_new_pid")))  # type:ignore

    return new_pid


def mint_new_ukrdcid(session: Session) -> str:
    """
    Placeholder function generate a random string for now

    Args:
        session (Session): _description_
    """
    return "".join(
        random.choice(string.ascii_uppercase + string.digits)  # nosec
        for _ in range(10)
    )


def generate_generic_key(parent: str, seq_no: Optional[int] = None) -> str:
    # not sure there is much point in this function
    return f"{parent}{KEY_SEPERATOR}{seq_no}"


def generate_key_laborder(laborder_xml: xsd_lab_orders, pid: str) -> str:
    # generate lab_order consitant with: https://github.com/renalreg/Data-Repository/blob/44d0b9af3eb73705de800fd52fe5a6b847219b31/src/main/java/org/ukrdc/repository/RepositoryManager.java#L679
    return f"{pid}{KEY_SEPERATOR}{laborder_xml.placer_id}"


def generate_key_resultitem(
    resultitem: sqla.ResultItem, order_id: str, seq_no: int
) -> str:
    """generates result item key. This is somewhat more complicated than some.
    https://github.com/renalreg/Data-Repository/blob/44d0b9af3eb73705de800fd52fe5a6b847219b31/src/main/java/org/ukrdc/repository/RepositoryManager.java#LL693C5-L693C5

    Args:
        resultitem (orm.ResultItem): _description_
        order_id (str): _description_
        seq_no (int): _description_
    """
    if resultitem.prepost == "PRE":
        return (
            f"{order_id}{KEY_SEPERATOR}{resultitem.service_id}{KEY_SEPERATOR}{seq_no}"
        )
    else:
        return f"{order_id}{KEY_SEPERATOR}{resultitem.prepost}{KEY_SEPERATOR}{resultitem.service_id}{KEY_SEPERATOR}{seq_no}"


def generate_key_dialysis_session(
    dialysis_session_xml: xsd_dialysis_sessions.DialysisSession,
    pid: str,
    seq_no: int = 0,
) -> str:
    procedure_time_uts = dialysis_session_xml.procedure_time.to_datetime().timestamp()
    procedure_type_code = dialysis_session_xml.procedure_type.code
    return f"{pid}{KEY_SEPERATOR}{procedure_time_uts}{KEY_SEPERATOR}{procedure_type_code}{KEY_SEPERATOR}{seq_no}"
