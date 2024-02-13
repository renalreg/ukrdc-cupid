from ukrdc_cupid.core.utils import DatabaseConnection  # type:ignore
from ukrdc_cupid.core.investigate.models import PatientID, Issue
from datetime import datetime
from typing import List, Tuple

# Connection to database containing issues
INVESTIGATE_SESSION = DatabaseConnection(env_prefix="INVESTIGATE").create_session(
    True, False
)


def get_patients(patient_ids: List[Tuple[str, str]]) -> List[PatientID]:
    patients = []

    for pid, ukrdcid in patient_ids:
        # Create a new patient instance
        patient = PatientID(ukrdcid=ukrdcid, pid=pid)

        # Attempt to retrieve the patient record from the database
        patient_record = (
            INVESTIGATE_SESSION.query(PatientID)
            .filter_by(ukrdcid=ukrdcid, pid=pid)
            .first()
        )

        if not patient_record:
            # If the patient doesn't exist, add the new patient to the session
            INVESTIGATE_SESSION.add(patient)

            # Commit the new patient to the database
            INVESTIGATE_SESSION.commit()

            # Refresh the session to get the new patient with the correct database-generated ID
            INVESTIGATE_SESSION.refresh(patient)

            # Assign the refreshed patient to patient_record
            patient_record = patient

        patients.append(patient_record)

    return patients


class Investigation:
    """The Investigation class uses a relatively simple model to link issues to
    pids/ukrdcids. We may wish to add extra fields to enhance the process of
    resolving the issues.
    """

    def __init__(self, patient_ids: List[Tuple[str, str]], issue_type_id: int) -> None:
        self.issue_type_id = issue_type_id
        self.patients: List[PatientID] = get_patients(patient_ids)
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
        INVESTIGATE_SESSION.add(new_issue)
        INVESTIGATE_SESSION.commit()

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
        INVESTIGATE_SESSION.commit()

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
