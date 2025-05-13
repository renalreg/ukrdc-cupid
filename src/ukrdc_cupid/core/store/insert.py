import time

from pydantic import BaseModel
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import text

from ukrdc_cupid.core.parse.xml_validate import SUPPORTED_VERSIONS
from ukrdc_cupid.core.parse.utils import load_xml_from_str
from ukrdc_cupid.core.store.models.ukrdc import PatientRecord
from ukrdc_cupid.core.store.models.structure import RecordStatus
from ukrdc_cupid.core.store.exceptions import (
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

import ukrdc_xsdata.ukrdc as xsd_ukrdc  # type: ignore

CURRENT_SCHEMA = max(SUPPORTED_VERSIONS)


class DataInsertionResponse(BaseModel):
    """
    Response model for data insertion operations
    """

    class Config:
        arbitrary_types_allowed = True

    new_records: int = 0
    deleted_records: int = 0
    unchanged_records: int = 0
    modified_records: int = 0
    identical_to_last: bool = False
    msg: str = ""
    errormsg: Optional[str] = None
    patient_record: Optional[PatientRecord] = None
    investigation: Optional[Investigation] = None

    def generate_insertion_summary(self) -> str:
        """
        Generate a summary table of insertion results.

        Returns:
            str: Formatted table as a string.
        """
        if (
            self.new_records == 0
            and self.unchanged_records == 0
            and self.modified_records == 0
        ):
            return ""

        total_records = (
            self.new_records
            + self.deleted_records
            + self.unchanged_records
            + self.modified_records
        )
        percentage_new = 100.0 * self.new_records / total_records

        table = (
            f"Records Summary\n"
            f"----------------\n"
            f"New Records: {self.new_records}\n"
            f"Deleted Records: {self.deleted_records}\n"
            f"Unchanged Records: {self.unchanged_records}\n"
            f"Modified Records: {self.modified_records}\n"
            f"Total Records: {total_records}\n"
            f"Percentage New Records: {percentage_new:.2f}%\n"
        )
        return table


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


@advisory_lock
def insert_incoming_data(
    ukrdc_session: Session,
    pid: str,
    ukrdcid: str,
    incoming_xml_file: xsd_ukrdc.PatientRecord,
    is_new: bool = False,
    mode: str = "full",
    debug: bool = False,
) -> dict:
    """Insert file into the database having matched to pid.
    do we need a no delete mode?

    Args:
        pid (str): _description_
        incoming_xml_file (xsd_ukrdc.PatientRecord): _description_
        no_delete (bool, optional): _description_. Defaults to False.
    """

    response = DataInsertionResponse()

    # load incoming xml file into cupid store models
    if mode == "ex-missing":
        patient_record = PatientRecord(xml=incoming_xml_file, ex_missing=True)
    else:
        patient_record = PatientRecord(xml=incoming_xml_file)

    # Map xml to rows in the database using cupid models this will produce a
    # tree of cupid models. These contain ukrdc_sqla models which can be
    # committed to the database to sync it to the incoming file.
    different_file = patient_record.map_to_database(
        session=ukrdc_session,
        ukrdcid=ukrdcid,
        pid=pid,
        is_new=is_new,
    )

    if not different_file:
        response.msg = f"Incoming file matched hash for last inserted file for pid = {pid}. No further data insertion has occurred."
        response.identical_to_last = True
        response.patient_record = patient_record
        return response

    # get the orm objects for the records that need to be created and add them
    # to the session
    orm_objects, counts = patient_record.get_orm_list()
    new = orm_objects[RecordStatus.NEW]
    ukrdc_session.add_all(new)

    response.new_records = counts[RecordStatus.NEW]
    response.modified_records = counts[RecordStatus.MODIFIED]
    response.unchanged_records = counts[RecordStatus.UNCHANGED]

    # get the orm objects for records not in the file
    records_for_deletion = patient_record.get_orm_deleted()
    for record in records_for_deletion:
        ukrdc_session.delete(record)

    response.deleted_records = len(records_for_deletion)

    # insert changes into database if valid
    error = commit_changes(ukrdc_session)
    if error is None:
        if is_new:
            response.msg = (
                f"Successfully created patient: pid = {pid}, ukrdcid = {ukrdcid}"
            )

        else:
            all_records = (
                response.modified_records
                + response.unchanged_records
                + response.new_records
            )
            new_records = 100.0 * response.new_records / all_records

            response.msg = f"Updated patient: pid = {pid}, ukrdcid = {ukrdcid}. {new_records:.2f}% of {all_records} records were new. {response.deleted_records} were new"
    else:
        if not is_new:
            # if the patient is in the database raise an investigation for a
            # human insight to figure out what is going on.
            investigation = Investigation(
                ukrdc_session,
                patient_ids=[(pid, ukrdcid)],
                issue_type_id=8,
                error_msg=str(error),
            )
            investigation.append_extras(xml=incoming_xml_file)
            response.errormsg = f"Patient could not be updated due to error:\n{error}\n"
            response.errormsg += (
                f"See investigation id = {investigation.issue.id} for more details"
            )
            response.investigation = investigation

        else:
            # TODO: Alternatively create a patient using the minimum possible
            # information (probably the contents of the patient_demog) and
            # raise and attach an investigation to that.
            raise DataInsertionError(
                f"New patient could not be inserted due to error- {error}"
            )

    response.patient_record = patient_record
    return response


def process_file(
    xml_body: str,
    ukrdc_session: Session,
    mode: str = "full",
    validate: bool = False,
    check_current_schema: bool = False,
) -> str:
    """Takes an xml file as a string and
    applies the cupid matching algorithm to attempt uploading it to the
    database.

    Args:
        xml_body (str): xml file as a string
        ukrdc_session (Session): ukrdc4 database session
    """

    # async def load_xml(mode: str, xml_body: str = Depends(_get_xml_body)):
    # Load XML and check it
    t0 = time.time()

    xml_object = load_xml_from_str(
        xml_body, validate=validate, check_current_schema=check_current_schema
    )

    print(f"Time to load file {time.time()-t0}")

    # identify patient
    patient_info = read_patient_metadata(xml_object)
    pid, ukrdcid, investigation = identify_patient_feed(
        ukrdc_session=ukrdc_session,
        patient_info=patient_info,
    )

    # if an investigation has been raised in identifying the patient we do not insert
    # This can be force merged if the incoming file is correct
    if investigation:
        investigation.create_issue()
        investigation.append_extras(xml=xml_body, metadata=patient_info)
        msg = "Writing to patient blocked by outstanding investigation"
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

    if mode == "clear":
        # delete patient before inserting data
        if not is_new:
            ukrdc_session.delete(PatientRecord(pid=pid))
            ukrdc_session.flush()

    print(f"Time to load validate and match {time.time()-t0}")

    # insert into the database
    response = insert_incoming_data(
        ukrdc_session=ukrdc_session,
        pid=pid,
        ukrdcid=ukrdcid,
        incoming_xml_file=xml_object,
        is_new=is_new,
        mode=mode,
        debug=True,
    )

    # Any investigation at this point will be associated with a merge to
    # a single patient record therefore there will be a single pid and
    # ukrdc id associated with it. Are we potentially storing data that
    # cause problems if the record gets anonymised?
    if investigation:
        # should this be an inbuilt method?
        patient = get_patients((pid, ukrdcid))  # type : ignore
        response.investigation.append_patients(patient)
        issue_id = response.investigation.issue.issue_id
        if not response.errormsg:
            msg = f"New patient was uploaded successfully but there was an issue in linking to ukrdc data check issue id: {issue_id} for more details.\n"
            msg += response.generate_insertion_summary()
        else:
            msg = f"New patient contains linkage issues simultaneously cannot be inserted. Check issue id: {issue_id} for more details."

    # add output response from committing the data to the general output
    if response.errormsg:
        msg = "File upload failed : " + response.errormsg
    else:
        msg = f"File successfully written to patient with pid = {pid} and ukrdcid = {ukrdcid}: \n"
        msg = msg + response.generate_insertion_summary()

    print(msg)
    print(f"That took {time.time() - t0:.2f} secs")

    return msg
