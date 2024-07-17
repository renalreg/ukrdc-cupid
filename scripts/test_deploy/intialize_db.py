from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ukrdc_sqla.ukrdc import (
    Base as UKRDC3Base,
)  # Adjust the import based on your application structure
from dotenv import load_dotenv
from ukrdc_cupid.core.investigate.models import Base as InvestiBase
import os
import glob

# local dir
DIR = os.path.join("scripts", "test_deploy")

# Load environment variables from .env.test file in the config subdirectory
load_dotenv(os.path.join(DIR, ".env.test"))

# Get the database URL from environment variables
db_url = os.getenv("DB_URL")

# Create the engine and session at some point we can pop the output of pg_dump
# into the sql folder and skip these steps
engine = create_engine(db_url)
UKRDC3Base.metadata.create_all(engine)
ukrdc_sessionmaker = sessionmaker(bind=engine)

# Create schema for investigations using models
InvestiBase.metadata.create_all(bind=engine)

# Make sequences to generate pid and ukrdcid
with ukrdc_sessionmaker() as session:
    sql_files = glob.glob(os.path.join("sql_scripts", "*.sql"))
    for file_path in sql_files:
        with open(file_path, 'r') as file:
            sql_script = file.read()    
            session.execute(sql_script)
    
    session.commit()