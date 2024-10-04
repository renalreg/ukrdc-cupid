"""Simple script to throw files from a folder directly at the cupid process
"""


import glob
import os
import shutil
from time import time

from ukrdc_cupid.core.utils import UKRDCConnection
from ukrdc_cupid.core.store.insert import process_file


# Configure 
SOURCE_FOLDER = ".xml_decrypted/*.xml"
PROCESSED_FOLDER = ".xml_to_load/loaded/"
DB_URL = "postgresql+psycopg://postgres:postgres@localhost:8008/ukrdc_test_docker"

files =  glob.glob(SOURCE_FOLDER)
connector = UKRDCConnection(url = DB_URL)
sessionmaker = connector.create_sessionmaker()
total_thinking_time = time() - time()
with sessionmaker() as session:
    for file_url in files[:100]:
        print(file_url)
        with open(file_url, encoding='utf-8') as f:
            xml_file = f.read()

        #process_file(xml_body=xml_file, ukrdc_session=session)
        try:
            # Process the file
            t0 = time()
            process_file(xml_body=xml_file, ukrdc_session=session)
            time_diff = time() - t0
            print(time_diff)
            total_thinking_time += time_diff
            # If successful, move the file to the processed folder
            new_location = os.path.join(PROCESSED_FOLDER, os.path.basename(file_url))
            shutil.move(file_url, new_location)
            print(f"Successfully processed and moved: {file_url} -> {new_location}")
        except Exception as e:
            # Log or print the exception if processing fails
            print(f"Failed to process {file_url}: {e}")
    print(total_thinking_time/100)