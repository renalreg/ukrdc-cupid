"""Simple script to throw files from a folder directly at the cupid process

Returns:
    _type_: _description_
"""


import glob
import os
import shutil
import requests
from pathlib import Path

from ukrdc_cupid.core.utils import UKRDCConnection
from ukrdc_cupid.core.store.insert import process_file



# Configure 
SOURCE_FOLDER = ".xml_errors/*.xml"
DB_URL = "postgresql://postgres:postgres@localhost:8008/ukrdc_test_docker"

files =  glob.glob(SOURCE_FOLDER)
connector = UKRDCConnection(url = DB_URL)
sessionmaker = connector.create_sessionmaker()
with sessionmaker() as session:
    for file_url in files:
        print(file_url)
        with open(file_url, encoding='utf-8') as f:
            xml_file = f.read()
            #try:
            process_file(xml_body=xml_file, ukrdc_session=session) 
            #except Exception as e:
            #    print(e)