import json

from ukrdc_cupid.core.investigate.models import PatientID, Issue, XmlFile
from ukrdc_cupid.core.parse.utils import load_xml_from_str, hash_xml

from datetime import datetime
from typing import List, Tuple, Union
from sqlalchemy.orm import Session
from sqlalchemy import select
from xsdata.formats.dataclass.serializers import XmlSerializer
import ukrdc_xsdata.ukrdc as xsd_ukrdc  # type: ignore

serializer = XmlSerializer()


def get_patients(
    session: Session, patient_ids: List[Tuple[str, str]]
) -> List[PatientID]:
    """The philosophy here is that every patient that raises a investigation
    will reference a patient which exists in the database already. Any patient
    the doesn't will be flagged as new. It may not be a unique patient record
    or in the case of an ukrdcid investigation one that has only just been
    generated.

    Args:
        session (Session): _description_
        patient_ids (List[Tuple[str, str]]): _description_

    Returns:
        List[PatientID]: _description_
    """
    patients = []

    for pid, ukrdcid in patient_ids:
        # Create a new patient instance
        patient = PatientID(ukrdcid=ukrdcid, pid=pid)

        # Attempt to retrieve the patient record from the database
        patient_record = (
            session.query(PatientID).filter_by(ukrdcid=ukrdcid, pid=pid).first()
        )

        if not patient_record:
            # If the patient doesn't exist, add the new patient to the session
            session.add(patient)

            # Commit the new patient to the database
            session.commit()

            # Refresh the session to get the new patient with the correct database-generated ID
            session.refresh(patient)

            # Assign the refreshed patient to patient_record
            patient_record = patient

        patients.append(patient_record)

    return patients


class Investigation:
    """The Investigation class uses a relatively simple model to link issues to
    pids/ukrdcids. We may wish to add extra fields to enhance the process of
    resolving the issues.
    """

    def __init__(
        self,
        session: Session,
        patient_ids: List[Tuple[str, str]],
        issue_type_id: int,
        is_blocking: bool = True,
        error_msg: str = None,
    ) -> None:
        self.issue_type_id = issue_type_id
        self.patients: List[PatientID] = get_patients(session, patient_ids)
        self.session = session
        self.issue: Issue = self.create_issue(
            is_blocking=is_blocking, error_msg=error_msg
        )

    def create_issue(self, is_blocking: bool = True, error_msg=None) -> Issue:
        """Function creates a new issue and adds it to the DB then returns
        it.

        Returns:
            Issue: issue record for the cupid investigations db
        """

        # create issue and link to patients via PatientIDToIssue
        today = datetime.now()
        new_issue = Issue(
            issue_id=self.issue_type_id,
            date_created=today,
            patients=self.patients,
            is_blocking=is_blocking,
            error_message=error_msg,
        )

        # Link the issue to patients
        self.session.add(new_issue)
        self.session.commit()

        return new_issue

    def append_extras(
        self,
        xml: Union[str, xsd_ukrdc.PatientRecord] = None,
        filename: str = None,
        metadata: dict = None,
    ) -> None:
        """Add some high level bits to the issue if file has been diverted

        Args:
            xml (str): Full xml file as a string. This will be reprocessed.
            filename (str): Name of the xml file (this may be opaque on the
            other side of MIRTH)
        """

        # look up xml file and append the issue to it if it exists or create it
        # if not. TODO: Look into doing things like stripping out file sent
        # date to avoid it being to pedantic about what it counts as a new
        # file.
        if xml is not None:
            if isinstance(xml, str):
                xml_obj, _ = load_xml_from_str(xml)
            else:
                xml_obj = xml
                xml = serializer.render(xml_obj)

            if not isinstance(xml_obj, xsd_ukrdc.PatientRecord):
                raise Exception("No bueno hombre")

            xml = xml.strip(" ").strip("\n")
            xml_file_hash = hash_xml(xml_obj)
            xml_file = self.session.execute(
                select(XmlFile).filter_by(file_hash=xml_file_hash)
            ).scalar_one_or_none()

            if xml_file is None:
                xml_file = XmlFile(file=xml, file_hash=xml_file_hash)

            self.session.add(xml_file)
            self.session.flush()
            self.issue.xml_file_id = xml_file.id

        if filename is not None:
            self.issue.filename = filename  # type:ignore

        if metadata is not None:
            # change datetimes to strings
            metadata_str = {
                k: v.isoformat() if isinstance(v, datetime) else v
                for k, v in metadata.items()
            }
            self.issue.attributes = json.dumps(metadata_str, indent=4)

        self.session.commit()

        return

    def append_patients(self, patients: list) -> None:
        """Sometimes the patient hasn't been created when the issue is
        raised and you may want to create it later. For example a new
        patient with a ukrdcid validation error would have a new pid
        minted

        Args:
            patients (List[PatientID]): _description_
        """
        for patient in patients:
            if patient not in self.issue.issue_to_patients:
                self.issue.issue_to_patients.append(patient)
        return
