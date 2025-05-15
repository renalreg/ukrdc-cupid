# CUPID Parse

Code relating to parsing incoming RDA XML strings. This submodule is likely to be minimal in functionality as `ukrdc_xsdata` does most of the heavy lifting here.

Down the line, we may want to move the basic RDA Validation functionality currently handled by `webapi`/`services` into this stage of the CUPID flow. This may then also lead onto more complex validation functionality such as warning and modifying, but not rejecting, files with minor issues like invalid postcodes.

## Input

- RDA XML string

## Output

- A single top-level `ukrdc_xsdata.ukrdc.PatientRecord` object
