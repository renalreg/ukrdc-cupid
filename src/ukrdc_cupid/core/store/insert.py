import time

from sqlalchemy.orm import Session
from sqlalchemy import text
from ukrdc_cupid.core.store.models.ukrdc import PatientRecord
from sqlalchemy.exc import OperationalError
from ukrdc_sqla.ukrdc import Base

import ukrdc_xsdata.ukrdc as xsd_ukrdc  # type: ignore
from typing import Optional, Tuple


def advisory_lock(func):
    def wrapper(ukrdc_session: Session, pid: str, *args, **kwargs):
        # this wrapper function applies for an advisory lock on a a particular pid
        # if it isn't available it will keep trying for up to 60 secs to obtain the lock

        start_time = time.time()
        max_wait_time = 60  # Maximum wait time in seconds

        while time.time() - start_time < max_wait_time:
            try:
                # Try to acquire an advisory lock for the specified pid
                ukrdc_session.execute(
                    text(f"SELECT pg_advisory_lock({int(pid)}::int)")
                )  # type:ignore

            except OperationalError as e:
                # Handle exceptions, log, or rollback if necessary
                print(f"Error: {e}")
                # session.rollback()
                # Wait for a short period before trying to acquire the lock again
                time.sleep(1)
                continue

            else:
                # Call the wrapped function
                result = func(ukrdc_session, pid, *args, **kwargs)

                # Release the advisory lock regardless of success or failure
                ukrdc_session.execute(
                    text(f"SELECT pg_advisory_unlock({int(pid)}::int)")
                )  # type:ignore
                return result

        # If the loop runs for the maximum wait time, raise an exception or handle accordingly
        raise TimeoutError("Unable to acquire advisory lock within the specified time.")

    return wrapper


@advisory_lock
def insert_incoming_data(
    ukrdc_session: Session,
    pid: str,
    ukrdcid: str,
    incoming_xml_file: xsd_ukrdc.PatientRecord,
    is_new: bool = False,
    debug: bool = False,
) -> Optional[Tuple[Base, Base, Base]]:  # type:ignore
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
    if debug:
        new = patient_record.get_orm_list(
            is_dirty=False, is_new=True, is_unchanged=False
        )
        dirty = patient_record.get_orm_list(
            is_dirty=True, is_new=False, is_unchanged=False
        )
        unchanged = patient_record.get_orm_list(
            is_dirty=False, is_new=True, is_unchanged=True
        )
    else:
        new = patient_record.get_orm_list(
            is_dirty=False, is_new=True, is_unchanged=False
        )

    # if patient record is new it needs to be added to session
    ukrdc_session.add_all(new)

    # get list of records to delete
    records_for_deletion = patient_record.get_orm_deleted()
    for record in records_for_deletion:
        ukrdc_session.delete(record)

    print("================================================")
    if is_new:
        print(f"Creating Patient: pid = {pid}, ukrdcid = {ukrdcid}")
    else:
        print(f"Updating Patient: pid = {pid}, ukrdcid = {ukrdcid}")

    print(f"New records: {len(ukrdc_session.new)}")
    print(f"Updated records: {len(ukrdc_session.dirty)}")

    try:
        ukrdc_session.flush()

        # in principle we could do a bunch of validation here before we commit
        ukrdc_session.commit()

    except Exception as e:
        print("we need some more sophisticated error handling here")
        print(e)
        ukrdc_session.rollback()

    if debug:
        return new, dirty, unchanged

    return None
