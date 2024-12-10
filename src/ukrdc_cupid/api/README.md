# CUPID API

This code contains the cupid api. This should be kept as simple as possible. It's not super clear where the functionality for cupid ends and ukrdc-fastapi especially when it comes to manually changing and manipulating records in the UKRDC. The semantics of the API mirrors the core repo.

## Features

- **Validate XML Files**: Validate RDA XML files against specific UKRDC schema versions.
- **Upload Patient Records**: Insert and store XML patient data into the UKRDC database.
- **Modify Patient Records**: Update, merge, or split UKRDC IDs associated with patient feeds.
- **Force Upload of Quarantined Files**: Reprocess quarantined files with specific issue IDs.
- **Delete Patient Records**: Remove patient feeds from the UKRDC database.

## API Endpoints

### 1. Validate XML

**Endpoint**: `/parse/xml_validate/{schema_version}`  
**Method**: `POST`  
Validates the provided XML file against the specified UKRDC RDA schema version.

- **Params**:
  - `schema_version` (str): Schema version to validate against.
- **Body**: XML data (must be of type `application/xml`).
- **Response**: Success message or list of validation errors.

### 2. Upload Patient File

**Endpoint**: `/store/upload_patient_file/{mode}`  
**Method**: `POST`  
Uploads and stores the provided XML patient file in the UKRDC database.

- **Params**:
  - `mode` (str): Upload mode. The options are as follows:

  | Mode | Description |
  |------|-------------|
  | full |             |
  | ex-missing |       |
  | clear |            |
  
  These have yet to be implemented.
- **Body**: XML data (must be of type `application/xml`).
- **Response**: Success message or error details.

### 3. Modify UKRDC ID (Split/Merge)

**Endpoint**: `/modify/ukrdcid`  
**Method**: `POST`  
Splits or merges patient feeds based on the provided UKRDC ID.

- **Params**:
  - `pid` (str): Patient ID.
  - `ukrdcid` (str, optional): UKRDC ID to merge with. If not provided, a new UKRDC ID is minted.
- **Response**: Success message or error details.

### 4. Force Upload Quarantined File

**Endpoint**: `/modify/force_merge_file/{issue_id}/{domain_pid}`  
**Method**: `POST`  
Resolve investigation by force uploading quarantined files to a specified domain pid. For example a issue may have been raised because the demographics couldn't confidently be verified however they have since been manually verified we wish to overwrite a given patient.

- **Params**:
  - `issue_id` (str): Issue identifier of the quarantined file.
  - `domain_pid` (str): Domain patient ID or `mint` to generate a new patient ID.
- **Response**: Success message or error details.

### 5. Delete Patient Record

**Endpoint**: `/modify/delete_patient/{domain_pid}`  
**Method**: `POST`  
Deletes a patient feed from the database.

- **Params**:
  - `domain_pid` (str): Domain patient ID to be deleted.
- **Response**: Success message with deleted patient identifiers.
