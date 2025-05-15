# CUPID Match

Code relating to record _matching_ specifically. In essence, given an RDA `xsdata` object (see `parse` submodule), determine the PID and UKRDC ID to use when storing the incoming record. Current working version preferably matches on patient numbers (NHS, CHI, HSC), if no patient numbers are provided in the xml file it matches on name and date of birth. 

## Input

- A single top-level `ukrdc_xsdata.ukrdc.PatientRecord` object

## Output

- Record PID string
- Record UKRDCID string

## Side-effects

- Database rows for work items raised during matching
  - **Note:** The exact form of these new work items is TBD, however they will be entirely different in form and meaning to our existing work items, requiring new tables (or an entirely separate database). Perhaps we should consider calling them something new, to make this clearer?

