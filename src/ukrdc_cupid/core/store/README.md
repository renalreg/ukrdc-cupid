# CUPID Store

Code relating to:

- The mapping of a top-level `ukrdc_xsdata.ukrdc.PatientRecord` object into `ukrdc_sqla` ORM objects
- The generation of primary keys the whole way down the tree of ORM objects
  - Using primary key generation to determine if ORM objects should be inserted, or update existing rows
- The insersion/updating of ORM objects into the UKRDC database

## Input

- Record PID string
- Record UKRDCID string
- A top-level `ukrdc_xsdata.ukrdc.PatientRecord` object

## Output

- None (though `ukrdc_sqla` ORM objects are created intermediately)

## Side-effects

- Insersion/updating of the incoming file into the UKRDC database
