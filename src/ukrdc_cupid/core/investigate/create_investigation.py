from ukrdc_cupid.core.investigate.models import PatientID, Issue
from datetime import datetime
from typing import List, Tuple
from sqlalchemy.orm import Session


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
        self, session: Session, patient_ids: List[Tuple[str, str]], issue_type_id: int
    ) -> None:
        self.issue_type_id = issue_type_id
        self.patients: List[PatientID] = get_patients(session, patient_ids)
        self.session = session
        self.issue: Issue = self.create_issue()

    def create_issue(self) -> Issue:
        """Function creates a new issue and adds it to the DB then returns
        it.

        Returns:
            Issue: issue record for the cupid investigations db
        """

        # create issue and link to patients via PatientIDToIssue
        today = datetime.now()
        new_issue = Issue(
            issue_id=self.issue_type_id, date_created=today, patients=self.patients
        )

        # Link the issue to patients
        self.session.add(new_issue)
        self.session.commit()

        return new_issue

    def append_file(self, xml: str, filename: str) -> None:
        """Add some high level bits to the issue if file has been diverted

        Args:
            xml (str): Full xml file as a string. This will be reprocessed.
            filename (str): Name of the xml file (this may be opaque on the
            other side of MIRTH)
        """
        # append xml and filename to issue
        self.issue.xml = xml
        self.issue.filename = filename  # type:ignore
        self.session.commit()

        return

    def append_patients(self, patients: list) -> None:
        """Sometimes the patient hasn't been created when the issue is
        raised and you may want to create it later. For example a new
        patient with a ukrdcid validation error would have a new

        Args:
            patients (List[PatientID]): _description_
        """
        for patient in patients:
            if patient not in self.issue.issue_to_patients:
                self.issue.issue_to_patients.append(patient)

        return
