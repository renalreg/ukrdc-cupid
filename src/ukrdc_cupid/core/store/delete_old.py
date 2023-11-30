import ukrdc_sqla.ukrdc as sqla
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional


def delete_records(
    table: sqla.Base,
    session: Session,
    pid: Optional[str],
    exclude_ids: Optional[List[str]],
):
    """Generic function to delete a set of records from there host table based on the pid and a list of ids.

    Args:
        table (sqla.Base): _description_
        session (Session): _description_
        pid (str): _description_
        exclude_ids (Optional[List[str]]): _description_
    """

    if exclude_ids is not None and pid is None:
        records_to_delete = (
            session.query(table)
            .where(and_(table.id.not_in(exclude_ids), table.pid == pid))
            .all()
        )
    elif exclude_ids is None and pid is not None:
        records_to_delete = (
            session.query(table)
            .where(
                and_(
                    table.id.not_in(exclude_ids),
                )
            )
            .all()
        )
    else:
        records_to_delete = session.query(table).where(table.pid == pid).all()

    for record in records_to_delete:
        session.delete(record)


def delete_timebound_records(
    table: sqla.Base,
    session: Session,
    pid: Optional[str],
    exclude_ids: Optional[List[str]],
    start,
    stop,
):
    return


# a few ugly duckings need special handling
def delete_result_items():
    return


def delete_survey_children():
    return


# Map delete function to table name
SQL_DELETE = {
    "address": lambda session, pid, ids: delete_records(
        sqla.Address, session, pid, ids
    ),
    "allergy": lambda session, pid, ids: delete_records(
        sqla.Allergy, session, pid, ids
    ),
    "causeofdeath": lambda session, pid, _: delete_records(
        sqla.CauseOfDeath, session, pid
    ),
    "clinicalrelationship": lambda session, pid, ids: delete_records(
        sqla.ClinicalRelationship, session, pid, ids
    ),
    "contactdetail": lambda session, pid, ids: delete_records(
        sqla.ContactDetail, session, pid, ids
    ),
    "diagnosis": lambda session, pid, ids: delete_records(
        sqla.Diagnosis, session, pid, ids
    ),
    "dialysissession": lambda session, pid, ids: delete_records(
        sqla.DialysisSession, session, pid, ids
    ),
    "document": lambda session, pid, ids: delete_records(
        sqla.Document, session, pid, ids
    ),
    "encounter": lambda session, pid, ids: delete_records(
        sqla.Encounter, session, pid, ids
    ),
    # "familydoctor" : lambda session, pid, ids : delete_records(sqla.FamilyDoctor, session, pid, ids),
    "familyhistory": lambda session, pid, ids: delete_records(
        sqla.FamilyHistory, session, pid, ids
    ),
    # "familyhistory" : lambda session, pid, ids : delete_records(sqla.Level, session, pid, ids),
    "medication": lambda session, pid, ids: delete_records(
        sqla.Medication, session, pid, ids
    ),
    "name": lambda session, pid, ids: delete_records(sqla.Name, session, pid, ids),
    "observation": lambda session, pid, ids: delete_records(
        sqla.Observation, session, pid, ids
    ),
    "patientnumber": lambda session, pid, ids: delete_records(
        sqla.PatientNumber, session, pid, ids
    ),
    # "familyhistory" : lambda session, pid, ids : delete_records(sqla.Question, session, pid, ids),
    "renaldiagnosis": lambda session, pid, ids: delete_records(
        sqla.RenalDiagnosis, session, pid, ids
    ),
    # "familyhistory" : lambda session, pid, ids : delete_records(sqla.Score, session, ids),
    "socialhistory": lambda session, pid, ids: delete_records(
        sqla.SocialHistory, session, pid, ids
    ),
    "survey": lambda session, pid, ids: delete_records(sqla.Survey, session, pid, ids),
    "transplant": lambda session, pid, ids: delete_records(
        sqla.Transplant, session, pid, ids
    ),
    "transplantlist": lambda session, pid, ids: delete_records(
        sqla.TransplantList, session, pid, ids
    ),
    "treatment": lambda session, pid, ids: delete_records(
        sqla.Treatment, session, pid, ids
    ),
    "vascularaccess": lambda session, pid, ids: delete_records(
        sqla.VascularAccess, session, pid, ids
    ),
}

SQL_DELETE_TIME_BOUND = {}
