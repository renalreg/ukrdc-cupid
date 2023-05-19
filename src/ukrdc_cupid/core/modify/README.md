# CUPID Modify

Logic code for several post-storage operations, including:

- Update the UKRDC ID of a given PatientRecord
  - **Split:** Take a record/records that are part of a group with a given UKRDC ID, mint a new UKRDC ID and split the specified record/records into that new UKRDC ID group.
  - **Merge:** Take a record/records that are part of a group with a given UKRDC ID, and modify the UKRDC ID to merge them into another, existing UKRDC ID group.
- Convert patient record to opt-out
  - See our [Confluence docs](https://renalregistry.atlassian.net/wiki/spaces/SP/pages/2213249114/JTRACE+Replacement#Convert-patient-record-to-opt-out) for more specific information.
- *Likely more things in future*
