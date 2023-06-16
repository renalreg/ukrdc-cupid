from sqlalchemy import create_engine
from sqlalchemy.sql import text
from sqlalchemy.orm import sessionmaker
from ukrdc_sqla.ukrdc import Base as UKRDC3Base 

url = "postgresql://postgres:postgres@localhost:5432/dummy_ukrdc"
engine = create_engine(url, echo = True)

UKRDC3Base.metadata.create_all(bind=engine)

ukrdc3_sessionmaker = sessionmaker(bind=engine)
ukrdc3 = ukrdc3_sessionmaker()
create_sequence = """
CREATE SEQUENCE generate_new_pid
    START 1
    INCREMENT BY 1
    NO MAXVALUE
    NO CYCLE;

SELECT setval('generate_new_pid', (SELECT COALESCE(MAX(pid)::integer, 0) + 1 FROM patientrecord));

COMMENT ON SEQUENCE public.generate_new_pid
    IS 'Sequence to generate new pids should be initiated as the maxiumum pid';
"""
ukrdc3.execute(create_sequence)
ukrdc3.commit()

sequencies = ukrdc3.execute(text("SELECT * FROM pg_sequences;"))

for ting in sequencies:
    print(ting)

