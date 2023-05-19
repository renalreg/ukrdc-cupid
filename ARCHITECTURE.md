# UKRDC-CUPID Architecture

- [core](#core)
  - [core/match](#core-match)
  - [core/store](#core-store)
    - [core/store/models](#core-store-models)
  - [core/parse](#core-parse)
  - [core/modify](#core-modify)
  - [core/inquire](#core-inquire)
- [api](#api)

<a name="core"></a>

## CUPID Core

All core logic for CUPID functionality. This should only contain code _used by_ the API, but no API/application-specific code.

Essentially everything in `core` should, in principle, be able to operate as a useful library in other projects. It's not clear if we'll allow/encourage this, but it demonstrates the separation we're aiming for.

### Basic flow

| Stage | Submodule | Input | Output | Side effects |
| ----- | --------- | ----- | ------ | ------------ |
| 1   | `parse`  | RDA XML string | `ukrdc_xsdata.ukrdc.PatientRecord` object | None |
| 2   | `match`  | `ukrdc_xsdata.ukrdc.PatientRecord` object | PID<br>UKRDCID<br>`ukrdc_xsdata.ukrdc.PatientRecord` object | Work items for matching issues added to database |
| 3   | `store`  | PID<br>UKRDCID<br>`ukrdc_xsdata.ukrdc.PatientRecord` object | None | Insersion/updating of the incoming file into the UKRDC database | 

We additionally include `modify` and `inquire` submodules, not part of the standard data flow.

The `modify` submodule handles logic for post-storage operations. See [`modify/README.md`](./modify/README.md) for more information.
The `inquire` submodule handles logic for auditing operations, and raising and resolving issues during the standard data flow. See [`inquire/README.md`](./inquire/README.md) for more information.

<a name="core-match"></a>

### CUPID Match

Code relating to record _matching_ specifically. In essence, given an RDA `xsdata` object (see `parse` submodule), determine the PID and UKRDC ID to use when storing the incoming record.

#### Input

- A single top-level `ukrdc_xsdata.ukrdc.PatientRecord` object

#### Output

- Record PID string
- Record UKRDCID string

#### Side-effects

- Database rows for work items raised during matching
  - **Note:** The exact form of these new work items is TBD, however they will be entirely different in form and meaning to our existing work items, requiring new tables (or an entirely separate database). Perhaps we should consider calling them something new, to make this clearer?


<a name="core-store"></a>

### CUPID Store

Code relating to:

- The mapping of a top-level `ukrdc_xsdata.ukrdc.PatientRecord` object into `ukrdc_sqla` ORM objects
- The generation of primary keys the whole way down the tree of ORM objects
  - Using primary key generation to determine if ORM objects should be inserted, or update existing rows
- The insersion/updating of ORM objects into the UKRDC database

#### Input

- Record PID string
- Record UKRDCID string
- A top-level `ukrdc_xsdata.ukrdc.PatientRecord` object

#### Output

- None (though `ukrdc_sqla` ORM objects are created intermediately)

#### Side-effects

- Insersion/updating of the incoming file into the UKRDC database

<a name="core-store-models"></a>

#### Storage Models

Contains *only* class definitions for our storage models, all subclassing `ukrdc_cupid.core.store.models.ukrdc.Node`.

*This may not need to be a whole directory if the models end up in a single file, however I'm structuring like this for now so we have the option to break the models file into smaller, domain-specific files if that ends up being useful.*

<a name="core-parse"></a>

### CUPID Parse

Code relating to parsing incoming RDA XML strings. This submodule is likely to be minimal in functionality as `ukrdc_xsdata` does most of the heavy lifting here.

Down the line, we may want to move the basic RDA Validation functionality currently handled by `webapi`/`services` into this stage of the CUPID flow. This may then also lead onto more complex validation functionality such as warning and modifying, but not rejecting, files with minor issues like invalid postcodes.

#### Input

- RDA XML string

#### Output

- A single top-level `ukrdc_xsdata.ukrdc.PatientRecord` object

<a name="core-modify"></a>

### CUPID Modify

Logic code for several post-storage operations, including:

- Update the UKRDC ID of a given PatientRecord
  - **Split:** Take a record/records that are part of a group with a given UKRDC ID, mint a new UKRDC ID and split the specified record/records into that new UKRDC ID group.
  - **Merge:** Take a record/records that are part of a group with a given UKRDC ID, and modify the UKRDC ID to merge them into another, existing UKRDC ID group.
- Convert patient record to opt-out
  - See our [Confluence docs](https://renalregistry.atlassian.net/wiki/spaces/SP/pages/2213249114/JTRACE+Replacement#Convert-patient-record-to-opt-out) for more specific information.
- *Likely more things in future*

<a name="core-inquire"></a>

### CUPID Inquire

The `inquire` submodule holds any logic relating to the inquiry and resolution of issues throughout the matching and storage process.

This includes (but may not be limited to):

- Raising and resolving matching issues (previously referred to as "Work Items")
  - See our [Confluence docs](https://renalregistry.atlassian.net/wiki/spaces/SP/pages/2213249114/JTRACE+Replacement#2.3-Work-Item:-Reject-file-for-existing-patient-record) for more information on what this will specifically involve.
- Raising and resolving validation _warnings_
  - This functionality has not yet been confirmed, but warnings raised by future validation rules in the `parse` submodule may be handled here. This is an open discussion.
- Audit records
  - As in `jtrace` and `data-repository`, we need to _strictly_ audit matching and storage of records. Raising and querying audit items may be handled here.

<a name="api"></a>

## CUPID API

Placeholder structure for the API application code. E.g. a FastAPI `app` instance and all the view classes etc.
