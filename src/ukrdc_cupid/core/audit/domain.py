"""
This module generates investigations which on records which have already been
inserted into the ukrdc. By cross checking in various ways or running specific
data quality reports it is designed to highlight ways in which the data can be
improved. 

Care should be taken to not link patients which have been unlinked by the opt
out process or other deliberate unlinkings.
"""
from ukrdc_cupid.core.audit.validate_matches import validate_demog_ukrdc


from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from sqlalchemy.orm import aliased
from ukrdc_sqla.ukrdc import PatientNumber, PatientRecord, Patient, Address, Name

# levenstein distance for fuzzy matchin this
SIMILARITY_THRESHOLD = 2

# Create aliases for table joins
PatientNumberAlias = aliased(PatientNumber)
PatientRecordAlias = aliased(PatientRecord)
PatientAlias = aliased(Patient)
AddressAlias = aliased(Address)
NameAlias = aliased(Name)


def close_matches_ukrdc(
    session: Session, match_generator_function, investigation_type: int
):
    """Meta function which allows us to validate and produce investigations for
    things that almost match. For example you could imagine an MRN which is
    mistyped and matched because it is similar.

    Args:
        session (Session): _description_
        match_generator_function (_type_): _description_
    """

    patient_records = match_generator_function(session)
    for pid_1, ukrdcid_1, dob_1, pid_2, ukrdcid_2 in patient_records:
        # cross validate records
        is_valid = validate_demog_ukrdc(session, dob_1, ukrdcid_2)

        # if successfully validated we raise an investigation
        if is_valid:

            # TODO: look up patients against issue investigations db
            # we need a mechanism for something like "this is a false positive"
            """
            Investigation(
                session=session,
                patient_ids=patient_ids,
                issue_type_id=investigation_type,
                is_blocking=False
            )
            """
    return


def mrn_similarity_matched(session):
    """This is really rather interesting from the number of collisions it is
    detecting one maybe this is just a birthday paradox type thing.

    Args:
        session (_type_): _description_

    Returns:
        _type_: _description_
    """

    # Select MRNs with specific types and calculate similarity between them
    stmt = (
        select(
            PatientRecord.pid,
            PatientRecord.ukrdcid,
            Patient.birthtime,
            PatientRecordAlias.pid,
            PatientRecordAlias.ukrdcid,
        )
        .select_from(PatientNumber)
        .join(PatientRecord, PatientRecord.pid == PatientNumber.pid)
        .join(Patient, Patient.pid == PatientRecord.pid)
        .join(
            PatientNumberAlias,
            and_(
                PatientNumber.patientid != PatientNumberAlias.patientid,
                PatientNumberAlias.organization == PatientNumber.organization,
            ),
        )
        .join(PatientRecordAlias, PatientNumberAlias.pid == PatientRecordAlias.pid)
        .join(PatientAlias, PatientAlias.pid == PatientRecordAlias.pid)
        .where(
            func.levenshtein(PatientNumber.patientid, PatientNumberAlias.patientid)
            < SIMILARITY_THRESHOLD,  # Similarity threshold
            PatientRecord.ukrdcid != PatientRecordAlias.ukrdcid,
            PatientRecord.sendingextract == "UKRDC",
            PatientNumber.organization.in_(["CHI", "HSC", "NHS"]),  # Filter MRN types
            PatientNumberAlias.organization.in_(["CHI", "HSC", "NHS"]),
        )
    )

    return [patient for patient in session.execute(stmt)]


def address_matched(session):
    """This joins patient on postcode with

    Args:
        session (_type_): _description_

    Returns:
        _type_: _description_
    """
    stmt = (
        select(
            Address.pid,
            PatientRecord.ukrdcid,
            Patient.birthtime,
            AddressAlias.pid,
            PatientRecordAlias.ukrdcid,
        )
        .select_from(Address)
        .join(PatientRecord, PatientRecord.pid == Address.pid)
        .join(Patient, Patient.pid == PatientRecord.pid)
        .join(AddressAlias, Address.postcode == AddressAlias.postcode)
        .join(PatientRecordAlias, AddressAlias.pid == PatientRecordAlias.pid)
        .where(
            PatientRecord.sendingextract == "UKRDC",
            PatientRecord.pid != PatientRecordAlias.pid,
            PatientRecord.ukrdcid != PatientRecordAlias.ukrdcid,
        )
    )
    return [patient for patient in session.execute(stmt)]


def name_matched_exact(session):
    """Exactly match on name and dob

    Args:
        session: Database session for executing the query.
    """
    stmt = (
        select(
            Name.pid,
            PatientRecord.ukrdcid,
            Patient.birthtime,
            NameAlias.pid,
            PatientRecordAlias.ukrdcid,
        )
        .select_from(Name)
        .join(PatientRecord, PatientRecord.pid == Name.pid)
        .join(Patient, Patient.pid == PatientRecord.pid)
        .join(
            NameAlias,
            and_(NameAlias.family == Name.family, NameAlias.given == Name.given),
        )
        .join(PatientRecordAlias, NameAlias.pid == PatientRecordAlias.pid)
        .join(PatientAlias, PatientAlias.pid == PatientRecordAlias.pid)
        .where(
            PatientRecord.sendingextract == "UKRDC",
            PatientRecord.pid != PatientRecordAlias.pid,
            PatientRecord.ukrdcid != PatientRecordAlias.ukrdcid,
            Patient.gender == PatientAlias.gender,
        )
    )

    return [patient for patient in session.execute(stmt)]


def name_matched_soundex(session):
    """Fuzzy match on name varients.

    Args:
        session: Database session for executing the query.
    """
    stmt = (
        select(
            Name.pid,
            PatientRecord.ukrdcid,
            Patient.birthtime,
            NameAlias.pid,
            PatientRecordAlias.ukrdcid,
        )
        .select_from(Name)
        .join(PatientRecord, PatientRecord.pid == Name.pid)
        .join(Patient, Patient.pid == PatientRecord.pid)
        .join(
            NameAlias,
            and_(
                func.soundex(NameAlias.family) == func.soundex(Name.family),
                func.soundex(NameAlias.given) == func.soundex(Name.given),
            ),
        )
        .join(PatientRecordAlias, NameAlias.pid == PatientRecordAlias.pid)
        .join(PatientAlias, PatientAlias.pid == PatientRecordAlias.pid)
        .where(
            PatientRecord.sendingextract == "UKRDC",
            PatientRecord.pid != PatientRecordAlias.pid,
            PatientRecord.ukrdcid != PatientRecordAlias.ukrdcid,
            Patient.gender == PatientAlias.gender,
        )
    )

    return [patient for patient in session.execute(stmt)]


def generate_domain_match_workitems(session):
    """Generate new matches by other means

    Args:
        session (_type_): _description_
    """

    # fuzzy match patient numbers
    close_matches_ukrdc(session, mrn_similarity_matched, 12)

    # match patients by address
    close_matches_ukrdc(session, address_matched, 11)

    # exact match name
    close_matches_ukrdc(session, name_matched_exact, 9)

    # fuzzy match name
    close_matches_ukrdc(session, name_matched_soundex, 10)


def generate_domain_data_issues(session):
    return
