# UKRDC-CUPID

## Status

Very much WIP. Proper docs and tests to come.

### Todo

- [ ] Finish basic conversion mapping
- [ ] Fix data conversions (e.g. datetimes and enums)
- [ ] Add convenience functions to convert an XML file (as opposed to an already-parsed XSData object)
- [ ] Add tests
- [ ] Add docs

## Developer notes

### Local Setup


### Build ARCHITECTURE.md

- Install `pipx`
- `pipx install archmd`
- `archmd src/ukrdc_cupid --out "ARCHITECTURE.md" --title="UKRDC-CUPID Architecture"`


## Naming

### Canonical name 1

**CUPID Universal Patient Identification** 

*CUPID* - This is the name of the application, and the application does some recursion

*Universal* - Matches across both systems within and between hospitals and feeds

*Patient Identification* - Handles matching files to records, and grouping records into patients


### Canonical name 2

**Consolidated Universal Patient Identification** 

*Consildated* - Doesn't rely on a separate EMPI database, all matching uses live UKRDC data

*Universal* - Matches across both systems within and between hospitals and feeds

*Patient Identification* - Handles matching files to records, and grouping records into patients
