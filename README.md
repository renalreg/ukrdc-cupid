# UKRDC-CUPID

Service to matchmake incoming xml files with patients in the ukrdc database.

## Status

In testing: the are probably loads of bits that have been missed but the current code can load xml files into a locally generated database spun up using the ukrdc-sqla models.

## Developer notes

### Local Setup

### Build ARCHITECTURE.md

- Install `pipx`
- `pipx install archmd`
- `archmd src/ukrdc_cupid --out "ARCHITECTURE.md" --title="UKRDC-CUPID Architecture"`

### Build with Docker

As of 07/10/24 a test version of cupid can be built with docker. This includes an api and a ukrdc built from the sqlalchemy models with a few modifications that cupid requires.

To fire this beast up run the following:

1. Build image:
`docker compose build --env-file=.env.docker`

2. Start up application:
`docker compose --env-file=.env.docker up -d`
note that there may be a bunch of errors.

3. Build/Rebuild database:
`docker compose --env-file=.env.docker run app python scripts/test_deploy/build_db.py`

This seperation of concerns allows you to do 2 without doing 3 and visa versa. This is kind of handy if for example you want to build a new version of cupid but want the 48 hours worth of data loading to persist from your last build.

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
