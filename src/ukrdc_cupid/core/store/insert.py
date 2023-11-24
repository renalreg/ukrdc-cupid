import ukrdc_sqla.ukrdc as sqla
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from datetime import datetime
from ukrdc_cupid.core.store.models.ukrdc import PatientRecord
from ukrdc_cupid.core.store.delete import SQL_DELETE

import ukrdc_xsdata.ukrdc as xsd_ukrdc  # type: ignore

from typing import List, Optional, Union


def insert_incoming_data(
    ukrdc_session: Session,
    pid: str,
    ukrdcid: str,
    incoming_xml_file: xsd_ukrdc.PatientRecord,
    is_new: bool = False,
):
    """Insert file into the database having matched to pid.
    do we need a no delete mode?

    Args:
        pid (str): _description_
        incoming_xml_file (xsd_ukrdc.PatientRecord): _description_
        no_delete (bool, optional): _description_. Defaults to False.
    """

    # load incoming xml file into cupid store models
    patient_record = PatientRecord(xml=incoming_xml_file)

    # map xml to rows in the database using the orm
    patient_record.map_to_database(
        session=ukrdc_session, ukrdcid=ukrdcid, pid=pid, is_new=is_new
    )

    # extract a list of records from cupid models
    incoming_records = patient_record.get_orm_list()
    ukrdc_session.add_all(incoming_records)

    # get list of records to delete
    records_for_deletion = patient_record.get_orm_deleted()
    for record in records_for_deletion:
        ukrdc_session.delete(record)

    # in principle we could do a bunch of validation here before we commit

    # flush and commit
    ukrdc_session.flush()

    ukrdc_session.commit()

def insert_into_sherlock(investigation, xml_object = None):
    """placeholder function for inserting workitems and processing diverted files
    """
    return