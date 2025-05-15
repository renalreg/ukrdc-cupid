# picklist of possible issues
ISSUE_PICKLIST = [
    [
        1,
        {
            "issue_type": "Demographic validation failure for feed Match",
            "is_domain_issue": False,
        },
    ],
    [
        2,
        {
            "issue_type": "Ambiguous feed match: pid identified via NI but not MRN",
            "is_domain_issue": False,
        },
    ],
    [
        3,
        {
            "issue_type": "Ambiguous feed match: matched to multiple persistent PIDs",
            "is_domain_issue": False,
        },
    ],
    [
        4,
        {
            "issue_type": "Ambiguous feed match: MRN matches disagree with NI matches",
            "is_domain_issue": False,
        },
    ],
    [
        5,
        {
            "issue_type": "Demographic validation failure in cross feed matching",
            "is_domain_issue": False,
        },
    ],
    [
        6,
        {
            "issue_type": "Ambiguous cross feed match: multiple ukrdcids identified",
            "is_domain_issue": False,
        },
    ],
    [
        7,
        {
            "issue_type": "File upload is being blocked by outstanding investigations",
            "is_domain_issue": False,
        },
    ],
    [8, {"issue_type": "Error inserting data into database", "is_domain_issue": False}],
    [9, {"issue_type": "Patients matched on name", "is_domain_issue": True}],
    [
        10,
        {"issue_type": "Patients matched on name similarity", "is_domain_issue": True},
    ],
    [11, {"issue_type": "Patients matched on postcodes", "is_domain_issue": True}],
    [
        12,
        {
            "issue_type": "Patients matched on NHS number similarity",
            "is_domain_issue": True,
        },
    ],
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
