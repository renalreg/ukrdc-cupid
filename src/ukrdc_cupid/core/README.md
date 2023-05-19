# CUPID Core

All core logic for CUPID functionality. This should only contain code _used by_ the API, but no API/application-specific code.

Essentially everything in `core` should, in principle, be able to operate as a useful library in other projects. It's not clear if we'll allow/encourage this, but it demonstrates the separation we're aiming for.

## Basic flow

| Stage | Submodule | Input | Output | Side effects |
| ----- | --------- | ----- | ------ | ------------ |
| 1   | `parse`  | RDA XML string | `ukrdc_xsdata.ukrdc.PatientRecord` object | None |
| 2   | `match`  | `ukrdc_xsdata.ukrdc.PatientRecord` object | PID<br>UKRDCID<br>`ukrdc_xsdata.ukrdc.PatientRecord` object | Work items for matching issues added to database |
| 3   | `store`  | PID<br>UKRDCID<br>`ukrdc_xsdata.ukrdc.PatientRecord` object | None | Insersion/updating of the incoming file into the UKRDC database | 
| (4) | `modify` | Varies | None | Varies |

Stage 4 is not part of the standard data flow, but rather handles logic for post-storage operations. See [`modify/README.md`](modify/README.md) for more information.