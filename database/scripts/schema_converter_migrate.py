"""
Script to cut over data from the schema converter cache to the upgraded ukrdc 
database. 
"""

from sqlalchemy import create_engine, text, select
from sqlalchemy.orm import sessionmaker
from ukrdc_sqla.ukrdc import PatientRecord, PatientNumber, Assessment, DialysisPrescription

def map_id_to_pid(ukrdc_session, cache_conn):
    """Function to match the patient id in the cache to the patientrecords in
    the ukrdc. 

    Args:
        ukrdc_session (_type_): _description_
        cache_conn (_type_): _description_

    Raises:
        Exception: _description_
    """

    # Query to get patient records from cache
    cache_query = text("""
        SELECT id, patientid, numbertype, organization 
        FROM patient;
    """)


    cache_results = cache_conn.execute(cache_query)

    id_lookups = {}  # Dictionary to store mappings


    for row in cache_results:
        # make a mapping between converter patient ids and pids
        cache_id = row[0]
        patient_number = row[1]
        number_type = row[2]
        organization = row[3]

        query = (
            select(PatientNumber)
            .join(PatientRecord, PatientRecord.pid == PatientNumber.pid)
            .where(
                PatientNumber.patientid == patient_number,
                PatientNumber.numbertype == number_type,
                PatientNumber.organization == organization,
                PatientRecord.sendingfacility == SENDING_FACILITY,
                PatientRecord.sendingextract == "UKRDC"
            )
        )

        results = ukrdc_session.execute(query).scalars().all()
        if len(results) >1:
            raise Exception("Ambiguous match in converter")
        elif len(results) == 1:
            id_lookups[cache_id] = results[0].pid
        else:
            id_lookups[cache_id] = None

    return id_lookups


def map_assessments(ukrdc_session, cache_conn, id_map):
    """Function to map between the assessments table in the cache and ukrdc
    """

    #grab assessments  
    # Query to get patient records from cache
    query = text("""
        SELECT * 
        FROM assessment
        ORDER BY update_date ASC;             
    """)


    results = [result for result in cache_conn.execute(query)]
    for result in results:
        pid = id_map.get(result[0])
        if pid is not None:
            # construct compound key since we have lost the order they arrived
            # in we may have to have a slightly different key
            ass_type = result[6]
            start_date = result[4]
            key = f"{pid}:{ass_type}:{start_date}"
            ukrdc_session.add(
                Assessment(
                    id = key, 
                    pid = pid, 

                    assessmentstart = start_date,
                    assessmentend = result[5],

                    assessmenttypecode = ass_type,
                    assessmenttypecodestd = result[7],
                    assessmenttypecodedesc = result[8],

                    assessmentoutcomecode = result[9],
                    assessmentoutcomecodestd = result[10],
                    assessmentoutcomecodedesc = result[11]
                )
            )

            try:
                ukrdc_session.commit() 
            except Exception as e: 
                print(e)

    return 

def map_dialysis_prescription(ukrdc_session, cache_conn, id_map):
    """
    Function to map and migrate dialysis prescription data from the cache to the UKRDC database.

    Args:
        ukrdc_session: SQLAlchemy session for the UKRDC database.
        cache_conn: Connection to the cache database.
        id_map: Dictionary mapping cache IDs to UKRDC patient PIDs.
    """

    # Query to get dialysis prescriptions from the cache 
    query = text("SELECT * FROM dialysisprescription")

    # Execute the query and fetch results
    cache_results = cache_conn.execute(query)

    for result in cache_results:
        pid = id_map.get(result[1])  # Map cache ID to UKRDC PID

        if pid is not None:
            # Construct a unique key for the dialysis prescription
            key = f"{pid}:{result[2]}:{result[3]}"  # Using `fromtime` and `totime` for uniqueness

            # Create a new DialysisPrescription object
            dialysis_prescription = DialysisPrescription(
                id=key,
                pid=pid,
                fromtime=result[5],
                totime=result[6],
                sessiontype=result[7],
                sessionsperweek=result[8],
                timedialysed=result[9],
                vascularaccess=result[10],
                enteredon=result[4],
                update_date=result[3],
                creation_date=result[2],  # Use update_date as a fallback for creation_date if not provided
            )

            # Add the object to the session
            ukrdc_session.add(dialysis_prescription)

    # Commit the transaction
    try:
        ukrdc_session.commit()
    except Exception as e:
        ukrdc_session.rollback()
        print(f"Error committing dialysis prescriptions: {e}")

    return

def map_diagnosises():
    return

def map_cause_of_death():
    return

def map_renal_diagnosis():
    return 

# Database connection URLs
#UKRDC_URL = "postgresql+psycopg://postgres:postgres@localhost:7000/ukrdc4"
UKRDC_URL = "postgresql+psycopg://ukrdc:password123@localhost:7000/ukrdc4"

CACHE_URL = "sqlite:///database/.dump/store.sqlite"
SENDING_FACILITY = "RK7CC"

# Initialize session maker for UKRDC database
ukrdc_engine = create_engine(UKRDC_URL)
ukrdc_sessionmaker = sessionmaker(bind=ukrdc_engine)

# Connect to the cache database
cache_engine = create_engine(CACHE_URL)
with cache_engine.connect() as cache_conn:
    with ukrdc_sessionmaker() as ukrdc_session:
        # tempory workaround to make the sqla models work (look into more)
        ukrdc_session.execute(text('SET search_path to "extract";'))

        # get a mapping between the ids from the ukrdc and the cache
        id_map = map_id_to_pid(ukrdc_session, cache_conn)

        map_assessments(ukrdc_session, cache_conn, id_map)

        map_diagnosises()

        map_cause_of_death()

        map_renal_diagnosis()