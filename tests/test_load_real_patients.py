"""
Getting into danger territory here but I think it would be good to have an area
for testing with real patient data. Need to be very sure nothing is getting
committed though. Real patient data should only ever end up in the folder
.xml_to_load which is in the .gitignore so hopefully safe. 

Rather than create and drop a dummy database we have a persistent db this
allows the interrogate the effect of loading up the data. I suppose this is
really a more automated version of something similar in the scripts folder.
"""

import glob
import pytest

from ukrdc_cupid.core.parse.utils import load_xml_from_path
from ukrdc_cupid.core.general import process_file
from ukrdc_cupid.core.utils import DatabaseConnection
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists
from conftest import ukrdc_sessionmaker

XML_DIRECTORY = ".xml_to_load/*.xml"
PERSISTENT_URL = "postgresql://postgres:postgres@localhost:5432/test_ukrdc_new"

@pytest.fixture(scope="function")
def ukrdc_test_session_persistent():
    if not database_exists(PERSISTENT_URL):
        sessionmaker = ukrdc_sessionmaker(url=PERSISTENT_URL, gp_info=True)
    else:
        sessionmaker = DatabaseConnection(url=PERSISTENT_URL).create_sessionmaker()
    
    with sessionmaker() as session:
        yield session


@pytest.mark.parametrize("xml_file", glob.glob(XML_DIRECTORY))
def test_load_xml_file_with_gp_info(ukrdc_test_session_persistent:Session, xml_file:str):
    # Specify the directory where your XML files are located
    xml_object = load_xml_from_path(xml_file)
    investigation = process_file(
        xml_object, 
        ukrdc_session=ukrdc_test_session_persistent, 
    )

    if investigation:
        # we add the file to the investigation it has been created
        investigation.append_file(
            xml = str(xml_object),
            filename = xml_file
        )