"""Module to combine and split records. In what instances would we have to
merge on pid. 
"""

from sqlalchemy.orm import Session
from ukrdc_sqla.ukrdc import PatientRecord
from ukrdc_cupid.core.store.keygen import mint_new_ukrdcid

from typing import List


def ukrdcid_split_merge(session: Session, pid: str, ukrdcid: str = None):
    """Function to change the ukrdcid of patient feed. Provide ukrdcid to merge
    with existing otherwise a new ukrdcid will be minted seperating record out
    from others with the same id.

    Args:
        pid (_type_): pid to identify feed to change the id of
        ukrdcid (str, optional): new ukrdcid if not supplied a new one will be minted
    """

    patientrecord = session.get(PatientRecord, pid)

    if not ukrdcid:
        ukrdcid = mint_new_ukrdcid(session=session)

    patientrecord.ukrdcid = ukrdcid
    session.commit()

    return


def pid_split_merge(session: Session, pids: List[str]):
    """Placeholder, not sure exactly if/how this will be needed but it is here
    just in case.

    Args:
        session (Session): _description_
        pids (List[str]): _description_
    """

    return


def force_merge_quarantined(session: Session, issueid: int, pid: str, ukrdcid: str):
    """Place holder to manually force a merge between a file which been put in
    quarantine because it is under investigation.
    """

    return
