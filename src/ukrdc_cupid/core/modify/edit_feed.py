"""Module to combine and split records. In what instances would we have to
merge on pid. 
"""

from sqlalchemy.orm import Session
from sqlalchemy import select
from ukrdc_sqla.ukrdc import PatientRecord
from ukrdc_cupid.core.store.keygen import mint_new_ukrdcid, mint_new_pid
from ukrdc_cupid.core.investigate.models import (
    Issue,
    XmlFile,
    PatientID,
    LinkPatientToIssue,
)
from ukrdc_cupid.core.parse.utils import load_xml_from_str
from ukrdc_cupid.core.store.insert import insert_incoming_data, process_file

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


def force_quarantined(
    session: Session,
    issueid: int,
    pid: str = None,
    process_blocked: bool = True,
    auto_resolve: bool = True,
):
    """Files which have been quarantined due to outstanding investigations may
    need to be force merged. This might mean they have been edited to clear any
    issues with them or it might be that the data in the database just needs
    overwriting. If the merge creates a new patient it will mint a new ukrdcid
    by default.
    """

    # retreive or mint ids
    if not pid:
        pid = mint_new_pid(session)
        # this can be changed with a seperate action
        ukrdcid = mint_new_ukrdcid(session)
        is_new = True
    else:
        is_new = False
        patient_record = session.get(PatientRecord, pid)
        if patient_record is None:
            raise Exception("helpful error message")

        ukrdcid = patient_record.ukrdcid

    # retrieve file based on id of issue
    issue_to_merge = session.get(Issue, issueid)
    if not issue_to_merge:
        raise Exception("helpful error message")

    xml_file_id = issue_to_merge.xml_file_id
    file_orm = session.get(XmlFile, xml_file_id)
    xml_file = load_xml_from_str(file_orm.file)

    # write to record with the specific pid
    # does exception need to be handled here?
    insert_incoming_data(session, pid, ukrdcid, xml_file, is_new)
    file_orm.is_reprocessed = True

    # auto resolve all blocking issues associated with the same file
    # (it's difficult to see how they could be resolved once it has been merged)
    if auto_resolve:
        for issue in file_orm.issues:
            issue.is_resolved = True

    # merge any files which have been held up this investigation
    if process_blocked:
        query_issue = (
            select(Issue)
            .join(LinkPatientToIssue, LinkPatientToIssue.c.issue_id == Issue.id)
            .join(PatientID, PatientID.id == LinkPatientToIssue.c.patient_id)
            .join(XmlFile, XmlFile.id == Issue.xml_file_id)
            # .join(PatientID)
            # .where(PatientID.pid == pid, Issue.date_created > issue_date)
            .order_by(Issue.date_created.asc())
        )

        issue_list = session.execute(query_issue).scalars().all()
        for issue in issue_list:
            # only try and reprocess blocking issues. Each file may have
            # multiple issues if multiple attempts to load it have been made
            # in reprocessing we close all these issues once the file is
            # is processed
            if issue.is_blocking:
                file = issue.xml_file
                if not file.is_reprocessed:
                    # process file if it fails an exception is triggered
                    _ = process_file(xml_body=file.file)
                else:
                    issue.is_resolved = True

            file.is_reprocessed = True
            # xml_file = issue

    return


def edit_quarantined(session: Session, issueid: int):
    """Allows an xml file which has been stored in the investigations schema to
    be edited.

    Args:
        session (Session): _description_
        issueid (int): _description_
    """
    return
