"""Simple script to throw files from a folder directly at the cupid process

"""


import glob
import os
import shutil

from ukrdc_cupid.core.utils import UKRDCConnection
from ukrdc_cupid.core.store.insert import process_file



# Configure 
SOURCE_FOLDER = ".xml_errored/*.xml"
PROCESSED_FOLDER = ".xml_errored/reprocessed/"
DB_URL = "postgresql://postgres:postgres@localhost:8008/ukrdc_test_docker"

files =  glob.glob(SOURCE_FOLDER)
connector = UKRDCConnection(url = DB_URL)
sessionmaker = connector.create_sessionmaker()
with sessionmaker() as session:
    for file_url in files:
        print(file_url)
        with open(file_url, encoding='utf-8') as f:
            xml_file = f.read()

        try:
            # Process the file
            process_file(xml_body=xml_file, ukrdc_session=session)
                
            # If successful, move the file to the processed folder
            new_location = os.path.join(PROCESSED_FOLDER, os.path.basename(file_url))
            shutil.move(file_url, new_location)
            print(f"Successfully processed and moved: {file_url} -> {new_location}")
        except Exception as e:
            # Log or print the exception if processing fails
            print(f"Failed to process {file_url}: {e}")