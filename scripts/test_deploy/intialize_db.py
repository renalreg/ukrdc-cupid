from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ukrdc_sqla.ukrdc import (
    Base as UKRDC3Base,
)  # Adjust the import based on your application structure
from dotenv import load_dotenv
import os

# local dir
DIR = os.path.join("scripts", "test_deploy")

# Load environment variables from .env.test file in the config subdirectory
load_dotenv(os.path.join(DIR, ".env.test"))

# Get the database URL from environment variables
db_url = os.getenv("DB_URL")

# Create the engine and session
engine = create_engine(db_url)
UKRDC3Base.metadata.create_all(engine)
ukrdc_sessionmaker = sessionmaker(bind=engine)

# Make sequences to generate pid and ukrdcid
# with open()
