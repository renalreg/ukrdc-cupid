# Load environment variables
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import dotenv_values

from ukrdc_cupid.core.audit.domain import (
    generate_domain_workitems,
)

ENV = dotenv_values(".env.scripts")
ukrdc_live_url = ENV["CUPID_URL"]
ukrdc_live_engine = create_engine(ukrdc_live_url)
LiveSession = sessionmaker(bind=ukrdc_live_engine, autoflush=False, autocommit=False)

with LiveSession() as live_session:
    # Patients = mrn_similarity_matched(session=live_session)
    generate_domain_workitems(session=live_session)
    # print(":)")
