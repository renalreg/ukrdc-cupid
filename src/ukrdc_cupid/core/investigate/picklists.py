# picklist of possible issues
ISSUE_PICKLIST = [
    [1, {"issue_type": "Demographic validation failure for feed Match"}],
    [2, {"issue_type": "Ambiguous feed match: pid identified via NI but not MRN"}],
    [3, {"issue_type": "Ambiguous feed match: matched to multiple persistent PIDs"}],
    [4, {"issue_type": "Ambiguous feed match: MRN matches disagree with NI matches"}],
    [5, {"issue_type": "Demographic validation failure in cross feed matching"}],
    [6, {"issue_type": "Ambiguous cross feed match: multiple ukrdcids identified"}],
    [7, {"issue_type": "File upload is being blocked by outstanding investigations"}],
    [8, {"issue_type": "Error inserting data into database"}],
]


STATUS_PICKLIST = [
    [1, {"status": "Open"}],
    [2, {"status": "Done"}],
    [3, {"status": "In Progress"}],
    [4, {"status": "In Review"}],
    [5, {"status": "Waiting for Unit"}],
    [6, {"status": "Pending Discussion"}],
    # to remove Non blocking status
    [7, {"status": "Status Downgraded"}],
]
