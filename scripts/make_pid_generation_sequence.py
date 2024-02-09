from sqlalchemy import create_engine
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from ukrdc_sqla.ukrdc import Base as UKRDC3Base 
from gp_auto_importer.main import auto 
from gp_auto_importer.database import ukrdc3_session


# import schemas


# add some sequences to automatically generate pids and ukrdcid
with ukrdc3_session() as ukrdc3:
    engine = ukrdc3.get_bind()

    UKRDC3Base.metadata.create_all(bind=engine)

    pid_sequence = """
    CREATE SEQUENCE generate_new_pid
        START 1
        INCREMENT BY 1
        NO MAXVALUE
        NO CYCLE;

    SELECT setval('generate_new_pid', (SELECT COALESCE(MAX(pid)::integer, 0) + 1 FROM patientrecord));

    COMMENT ON SEQUENCE public.generate_new_pid
        IS 'Sequence to generate new pids should be initiated as the maxiumum pid';
    """
    ukrdc3.execute(pid_sequence)

    ukrdc_sequence = """
    CREATE SEQUENCE generate_new_ukrdcid
        START 1
        INCREMENT BY 1
        NO MAXVALUE
        NO CYCLE;

    SELECT setval('generate_new_ukrdcid', (SELECT COALESCE(MAX(ukrdcid)::integer, 0) + 1 FROM patientrecord));

    COMMENT ON SEQUENCE public.generate_new_pid
        IS 'Sequence mints new ukrdcids';
    """
    ukrdc3.execute(ukrdc_sequence)


    ukrdc3.commit()

    sequencies = ukrdc3.execute(text("SELECT * FROM pg_sequences;"))

    for ting in sequencies:
        print(ting)

# import the gp codes
