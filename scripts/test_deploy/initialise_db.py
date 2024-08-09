"""Here we have a quick and dirty script to 
"""

import uvicorn

from ukrdc_cupid.core.utils import UKRDCConnection
from ukrdc_cupid.api.main import app, get_session
from sqlalchemy_utils import create_database
from dotenv import dotenv_values

from sqlalchemy.orm import Session

ENV = dotenv_values(".env.docker")
driver = ENV["UKRDC_DRIVER"]
user = ENV['UKRDC_USER']
password = ENV['UKRDC_PASSWORD']
port = ENV['UKRDC_PORT']
name = ENV['UKRDC_NAME']


# generate ukrdc database
db_url =  f"{driver}://{user}:{password}@db:{port}/{name}"
#db_url =  f"{driver}://{user}:{password}@localhost:{port}/{name}"
connector = UKRDCConnection(url=db_url)
connector.generate_schema(gp_info=True)

print("We have a database :)")

def get_session_docker() -> Session:
    sessionmaker = connector.create_sessionmaker()
    session = sessionmaker()
    try:
        yield session 
    finally:
        session.close()

# Override the dependency in the FastAPI app to connect to dockerised ukrdc
app.dependency_overrides[get_session] = get_session_docker

# Start the API server
uvicorn.run(app, host="0.0.0.0", port=8000)
