import ukrdc_sqla.ukrdc as sqla
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
from ukrdc_cupid.core.store.models.ukrdc import PatientRecord

import ukrdc_xsdata.ukrdc as xsd_ukrdc  # type: ignore

from typing import List, Optional, Union

# there might be a neater way of doing this mapping
SUPPORTED_SQLA = {
    "address": sqla.Address,
    "allergy": sqla.Allergy,
    "causeofdeath": sqla.CauseOfDeath,
    "clinicalrelationship": sqla.ClinicalRelationship,
    "contactdetail": sqla.ContactDetail,
    "diagnosis": sqla.Diagnosis,
    "name": sqla.Name,
    "patientrecord": sqla.PatientRecord,
    "patient": sqla.Patient,
}


def insert_records(
    ukrdc_session: Session,
    orm_class: sqla.Base,
    pid: str,
    incoming_records=List[sqla.Base],
    delete: bool = True,
):
    """The assumption is the patientrecord is sent in full every time
    https://renalregistry.atlassian.net/l/cp/VjGt07Ut
    with the exception of records with a supplied time range.
    The assumption here is that it is quicker to fetch all the records
    and match them locally. I get the impression this is not how sqla
    is designed to be used.
    """

    incoming_ids = [incoming_record.id for incoming_record in incoming_records]

    if delete:
        # load all existing records for pid, track ids and delete anything not in incoming file
        records_to_modify = (
            ukrdc_session.query(orm_class).where(orm_class.pid == pid).all()
        )
        existing_ids = [record.id for record in records_to_modify]
        records_to_delete = [
            record for record in records_to_modify if record.id not in incoming_ids
        ]
        for record in records_to_delete:
            ukrdc_session.delete(record)
    else:
        records_to_modify = (
            ukrdc_session.query(orm_class).where(orm_class.id.in_(incoming_ids)).all()
        )
        existing_ids = [record.id for record in records_to_modify]

    # iterate through incoming and update creation date if it already exists
    for incoming_record in incoming_records:
        if incoming_record.id in existing_ids:
            domain_record = records_to_modify[existing_ids.index(incoming_record.id)]
            incoming_record.creation_date = domain_record.creation_date
            # patient record uniquely has a repository created date
            if incoming_record.__tablename__ == "patientrecord":
                incoming_record.repositorycreationdate = (
                    domain_record.repositorycreationdate
                )
        else:
            if incoming_record.__tablename__ == "patientrecord":
                incoming_record.repositorycreationdate = (
                    incoming_record.repositoryupdatedate
                )

        ukrdc_session.merge(incoming_record)


def insert_time_bound(
    ukrdc_session: Session, records, start: datetime, stop: datetime, no_delete=False
):
    """
    Args:
        start (datetime): _description_
        stop (datetime): _description_
        no_delete (bool, optional): _description_. Defaults to False.
    """


def insert_incoming_data(
    ukrdc_session: Session,
    pid: str,
    ukrdcid: str,
    incoming_xml_file: xsd_ukrdc.PatientRecord,
    no_delete: bool = False,
):
    """Insert file into the database having matched to pid.

    Args:
        pid (str): _description_
        incoming_xml_file (xsd_ukrdc.PatientRecord): _description_
        no_delete (bool, optional): _description_. Defaults to False.
    """

    # load incoming xml file into cupid store models
    patient_record = PatientRecord(incoming_xml_file)
    patient_record.map_xml_to_tree()

    # transform records in the file to how they will appear in database
    patient_record.transform(pid=pid, ukrdcid=ukrdcid)

    # get records to be inserted in a linear form
    incoming_records = patient_record.get_contained_records()

    # iterate through merging the records
    for tablename, records in incoming_records.items():
        if tablename == "laborder":
            print("")
        elif tablename == "observation":
            print("")
        elif tablename == "dialysissessions":
            print("")
        else:
            sqla_orm = SUPPORTED_SQLA.get(tablename)
            if sqla_orm:
                insert_records(ukrdc_session, sqla_orm, pid, records)

    ukrdc_session.commit()
