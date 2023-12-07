from ukrdc_cupid.core.utils import DatabaseConnection
from ukrdc_cupid.core.investigate.models import PatientID, Issue
from datetime import datetime
from typing import List, Tuple, Literal

# Connection to database containing issues
INVESTIGATE_SESSION = DatabaseConnection(prefix="INVESTIGATE").create_session()

# picklist of possible issues
ISSUE_PICKLIST = Literal[
    "Demographic Validation Failure on PID Match", 
    "Ambiguous PID Match: matched on MRN but not NI",
    "Ambiguous PID Match: matched to multiple persitant PIDs",
    "Ambiguous PID Match: MRN matches disagree with NI matches",
    "Demographic Validation Failure on UKRDCID Match",
    "Ambiguous UKRDCID match: matched to multiple persistant UKRDCIDs" 
]

def get_patients(patient_ids: List[Tuple[str, str]]):
    patients = []
    
    for pid, ukrdcid in patient_ids:
        # Create a new patient instance
        patient = PatientID(ukrdcid=ukrdcid, pid=pid)

        # Attempt to retrieve the patient record from the database
        patient_record = INVESTIGATE_SESSION.query(PatientID).filter_by(ukrdcid=ukrdcid, pid=pid).first()

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

class Investigation():
    """The Investigation class uses a relatively simple model to link issues to
    pids/ukrdcids. We may wish to add extra fields to enhance the process of 
    resolving the issues.
    """
    def __init__(self, patient_ids:List[Tuple[str,str]], issue_type:ISSUE_PICKLIST):
        self.issue_type = issue_type
        self.patients = get_patients(patient_ids)
        self.issue:Issue

    def create_issue(self):
        # create issue and link to patients via PatientIDToIssue 
        """
        today = datetime.now()
        self.issue = Issue(
            issue_type=self.issue_type,
            date_created=today,
            error_message=self.issue_type,
            issue_to_patients=self.patients  # Link the issue to patients
        )
        INVESTIGATE_SESSION.add(self.issue)
        INVESTIGATE_SESSION.commit()
        """
        # create issue and link to patients via PatientIDToIssue 
        today = datetime.now()
        new_issue = Issue(
            issue_type=self.issue_type,
            date_created=today,
            error_message=self.issue_type,
        )
        
        # Link the issue to patients
        new_issue.issue_to_patients = self.patients
        INVESTIGATE_SESSION.add(new_issue)
        INVESTIGATE_SESSION.commit()

        self.issue = new_issue

    def append_file(self, xml:str, filename:str):
        # append xml and filename to issue
        self.issue.xml = xml
        self.issue.filename = filename
        INVESTIGATE_SESSION.commit()

    def append_patients(self, patients:List[PatientID]):
        for patient in patients:
            if patient not in self.issue.issue_to_patients:
                self.issue.issue_to_patients.append(patient)