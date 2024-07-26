from sqlalchemy.orm import Session
from ukrdc_cupid.core.investigate.models import IssueType

# picklist of possible issues
ISSUE_PICKLIST = [
    [1, "Demographic validation failure for feed Match"],
    [2, "Ambiguous feed match: pid identified via NI but not MRN"],
    [3, "Ambiguous feed match: matched to multiple persistent PIDs"],
    [4, "Ambiguous feed match: MRN matches disagree with NI matches"],
    [5, "Demographic validation failure in cross feed matching"],
    [6, "Ambiguous cross feed match: multiple ukrdcids identified"],
]


def update_issue_types(session: Session, issues: list = ISSUE_PICKLIST) -> None:
    """
    Update issue lookup table.
    Note: this needs to be checked to ensure its working/uptodate
    """
    for issue_id, issue_type in issues:
        issue = session.get(IssueType, issue_id)
        if issue:
            issue.issue_type = issue_type
        else:
            issue = IssueType(id=issue_id, issue_type=issue_type)
            session.add(issue)

    session.commit()
