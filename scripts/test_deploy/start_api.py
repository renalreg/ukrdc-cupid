"""
This is probably a non standard way of doing things but it seems to work. 
"""

from ukrdc_cupid.core.utils import UKRDCConnection
from ukrdc_cupid.api.main import app, get_session
from sqlalchemy.orm import Session
import uvicorn
from dotenv import dotenv_values


ENV = dotenv_values(".env.docker")
driver = ENV["UKRDC_DRIVER"]
user = ENV['UKRDC_USER']
password = ENV['UKRDC_PASSWORD']
port = ENV['UKRDC_PORT']
name = ENV['UKRDC_NAME']
host = ENV['UKRDC_HOST']

# db url
db_url =  f"{driver}://{user}:{password}@db:{port}/{name}"

connector = UKRDCConnection(url=db_url)
sessionmaker = connector.create_sessionmaker()
    
def get_session_docker() -> Session:
    with sessionmaker() as session:
        try:
            yield session 
        finally:
            session.close()

# Override the dependency in the FastAPI app to connect to dockerised ukrdc
app.dependency_overrides[get_session] = get_session_docker

# Start the API server
uvicorn.run(app, host="0.0.0.0", port=8000)