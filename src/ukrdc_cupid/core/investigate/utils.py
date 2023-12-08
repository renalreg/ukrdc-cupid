from ukrdc_cupid.core.investigate.models import IssueType
from ukrdc_cupid.core.utils import DatabaseConnection

from typing import List

# Connection to database containing issues
INVESTIGATE_SESSION = DatabaseConnection(env_prefix="INVESTIGATE").create_session()

# picklist of possible issues
ISSUE_PICKLIST = [
    [1, "Demographic Validation Failure on PID Match"],
    [2, "Ambiguous PID Match: matched on MRN but not NI"],
    [3, "Ambiguous PID Match: matched to multiple persitant PIDs"],
    [4, "Ambiguous PID Match: MRN matches disagree with NI matches"],
    [5, "Demographic Validation Failure on UKRDCID Match"],
    [6, "Ambiguous UKRDCID match: matched to multiple persistant UKRDCIDs"],
]


def update_issue_types(issues: List[List[int, str]] = ISSUE_PICKLIST) -> None:
    """
    Update issue lookup table
    """
    for issue_id, issue_type in issues:
        issue = INVESTIGATE_SESSION.get(IssueType, issue_id)
        if issue:
            issue.issue_type = issue_type
        else:
            issue = IssueType(issue_id=issue_id, issue_type=issue_type)
            INVESTIGATE_SESSION.add(issue)

    INVESTIGATE_SESSION.commit()
