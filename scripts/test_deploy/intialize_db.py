from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ukrdc_sqla.ukrdc import Base as UKRDC3Base  # Adjust the import based on your application structure


engine = create_engine('postgresql://postgres:postgres@db:5432/test_ukrdc_persistent')
UKRDC3Base.metadata.create_all(engine)
ukrdc_sessionmaker = sessionmaker(bind = engine)