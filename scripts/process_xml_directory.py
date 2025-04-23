"""Simple script to throw files from a folder directly at the cupid process
"""


import glob
import os
import shutil
from time import time
from ukrdc_cupid.core.store.insert import process_file
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Configure 
#SOURCE_FOLDER = ".xml_to_load/*.xml"
#PROCESSED_FOLDER = ".xml_to_load/"
SOURCE_FOLDER = "tests/xml_files/store_tests/*.xml"
PROCESSED_FOLDER ="tests/xml_files/store_tests/"

DB_URL = "postgresql+psycopg://postgres:postgres@localhost:8000/ukrdc4"
HANDLE_ERRORS = True

files =  glob.glob(SOURCE_FOLDER)

total_thinking_time = time() - time()
engine = create_engine(DB_URL)
sessionmaker = sessionmaker(bind=engine)
with sessionmaker() as session:
    for file_url in files:
        with open(file_url, "r", encoding="utf-8") as file:
            xml_file = file.read()

        # Process the file
        t0 = time()
        #if HANDLE_ERRORS:
        try:
            process_file(
                xml_body=xml_file, 
                ukrdc_session=session, 
                validate=False, 
                mode = "full",
                check_current_schema=False
            )
        except Exception as e:
            # Log or print the exception if processing fails
            msg = f"Failed to process {file_url}"
            if HANDLE_ERRORS:
                print(msg)
            else:
                raise Exception(msg) from e
            session.rollback()
            
        time_diff = time() - t0
        print(time_diff)
        total_thinking_time += time_diff
        # If successful, move the file to the processed folder
        new_location = os.path.join(PROCESSED_FOLDER, os.path.basename(file_url))
        shutil.move(file_url, new_location)
        print(f"Successfully processed and moved: {file_url} -> {new_location}")


    print(total_thinking_time/100)