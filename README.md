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

### Line length

For this repository (and _only_ this repository), we allow extra long lines.
This is because the schema maps are more readable if we have one element per line.
If we find in the future that this is causing issues for developers, we will consider re-introducing the line length limit.

For now, we effectively disable the line length limit by setting it to a large number:

`black --line-length=160 .`

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
