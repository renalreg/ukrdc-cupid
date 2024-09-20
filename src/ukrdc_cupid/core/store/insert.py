import time

from sqlalchemy.orm import Session
from sqlalchemy import text

from ukrdc_cupid.core.parse.xml_validate import SUPPORTED_VERSIONS
from ukrdc_cupid.core.parse.utils import load_xml_from_str
from ukrdc_cupid.core.store.models.ukrdc import PatientRecord
from ukrdc_cupid.core.store.exceptions import (
    SchemaVersionError,
    InsertionBlockedError,
    DataInsertionError,
)
from ukrdc_cupid.core.investigate.create_investigation import (
    get_patients,
    Investigation,
)
from ukrdc_cupid.core.store.keygen import mint_new_pid, mint_new_ukrdcid

from ukrdc_cupid.core.match.identify import (
    identify_patient_feed,
    read_patient_metadata,
    identify_across_ukrdc,
)

from sqlalchemy.exc import OperationalError
from ukrdc_sqla.ukrdc import Base

import ukrdc_xsdata.ukrdc as xsd_ukrdc  # type: ignore
from typing import Optional, Tuple

CURRENT_SCHEMA = max(SUPPORTED_VERSIONS)


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


def commit_changes(ukrdc_session: Session):
    """This function can be expanded in the future but it is to handle errors
    with things like foreign key violations.

    Args:
        ukrdc_session (Session): _description_
    """
    try:
        # we may want to add other validation steps here
        ukrdc_session.flush()
        ukrdc_session.commit()

    except Exception as e:
        # We may wish to generate more metadata here
        msg = e.args[0]
        # code = e.code
        errormsg = f"Error inserting data into database: {msg}"
        ukrdc_session.rollback()

        return errormsg


# @advisory_lock
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

    # insert changes into database if valid
    error = commit_changes(ukrdc_session)

    if error is None:
        print("================================================")
        if is_new:
            print(f"Creating Patient: pid = {pid}, ukrdcid = {ukrdcid}")
        else:
            print(f"Updating Patient: pid = {pid}, ukrdcid = {ukrdcid}")

        print(f"New records: {len(ukrdc_session.new)}")

        print(f"Updated records: {len(ukrdc_session.dirty)}")
    else:
        if not is_new:
            # if the patient is in the database raise a workitem
            investigation = Investigation(
                ukrdc_session,
                patient_ids=[(pid, ukrdcid)],
                issue_type_id=8,
                error_msg=str(error),
            )
            investigation.append_extras(xml=incoming_xml_file)

        else:
            # otherwise we raise an error this will usually be some sort of sql
            # statement. In theory I think the patient should still have their
            # demographics information inserted this allows it to be handled as
            # an investigation rather than an error.
            raise DataInsertionError(f"New patient could not be inserted - {error}")

    if debug:
        return new, dirty, unchanged

    return None


def process_file(xml_body: str, ukrdc_session: Session, mode: str = "full"):
    """Takes an xml file as a string and
    applies the cupid matching algorithm to attempt uploading it to the
    database

    Args:
        xml_object (PatientRecord): _description_
        ukrdc_session (Session): _description_
    """

    # The original specs contained several different insertion modes this
    # will probably need to be reflected here in some sort of way
    if mode == "full":
        # this does an update in which existing domain record is overwritten
        # with incoming
        pass

    elif mode == "ex-missing":
        # this mode doesn't delete records which are missing between the start
        # stop times for those records where everything isn't sent every time
        pass

    elif mode == "clear":
        # delete patient before inserting data
        pass

    # async def load_xml(mode: str, xml_body: str = Depends(_get_xml_body)):
    # Load XML and check it
    xml_object, xml_version = load_xml_from_str(xml_body)
    if xml_version < CURRENT_SCHEMA:
        msg = f"XML request on version {xml_version} but cupid requires version {CURRENT_SCHEMA}"
        raise SchemaVersionError(msg)

    # identify patient
    patient_info = read_patient_metadata(xml_object)
    pid, ukrdcid, investigation = identify_patient_feed(
        ukrdc_session=ukrdc_session,
        patient_info=patient_info,
    )

    # if an investigation has been raised in identifying the patient we do not insert
    # (we could introduce a force mode to make it try regardless)
    if investigation:
        investigation.create_issue()
        investigation.append_extras(xml=xml_body, metadata=patient_info)
        msg = "File could not successfully write to existing patient"
        raise InsertionBlockedError(msg)

    # generate new patient ids if required
    if not pid:
        pid = mint_new_pid(session=ukrdc_session)
        # Attempt to identify patient across the ukrdc
        ukrdcid, investigation = identify_across_ukrdc(
            ukrdc_session=ukrdc_session,
            patient_info=patient_info,
        )
        is_new = True
        if not ukrdcid:
            ukrdcid = mint_new_ukrdcid(session=ukrdc_session)
    else:
        # look up pid against investigations
        is_new = False

    # insert into the database
    insert_incoming_data(
        ukrdc_session=ukrdc_session,
        pid=pid,
        ukrdcid=ukrdcid,
        incoming_xml_file=xml_object,
        is_new=is_new,
        debug=True,
    )

    # Any investigation at this point will be associated with a merge to
    # a single patient record therefore there will be a single pid and
    # ukrdc id associated with it. Are we potentially storing data that
    # cause problems if the record gets anonomised?
    if investigation:
        # should this be an inbuilt method?
        patient = get_patients((pid, ukrdcid))  # type : ignore
        investigation.append_patients(patient)
        issue_id = investigation.issue.issue_id
        msg = f"New patient was uploaded successfully but there was an issue in linking to ukrdc data check issue id: {issue_id} for more details"
    else:
        msg = "File uploaded successfully"

    return msg
