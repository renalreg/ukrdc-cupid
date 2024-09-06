"""Simple script to throw files at the cupid api

Returns:
    _type_: _description_
"""


import glob
import os
import shutil
import requests
from pathlib import Path

# Configuration
SOURCE_FOLDER = Path(".xml_to_load")
DESTINATION_FOLDER = Path(".xml_to_load","loaded")
SERVER_URL = 'http://localhost:8000/store/upload_patient_file/full'

def post_xml(file_path: str):
    """Post XML file to the server."""
    with open(file_path, 'r') as file:
        content = file.read()  # Read the content of the XML file
        
    response = requests.post(
        SERVER_URL,
        data=content,
        headers={"Content-Type": "application/xml"}
    )
    return response

def move_file(file_path, destination_folder):
    """Move file to a different folder."""
    shutil.move(file_path, destination_folder)


# Use glob to find all XML files in the source folder
xml_files = glob.glob(os.path.join(SOURCE_FOLDER, '*.xml'))

print(f"Loading files in directory {SOURCE_FOLDER} via the cupid api, they will be moved to directory {DESTINATION_FOLDER}")


for file_path in xml_files:
    filename = os.path.basename(file_path)
    print(f'Processing {file_path}')
        
    # Post XML file to the server
    response = post_xml(file_path)
    print(response.content)
    print(f'Status Code: {response.status_code}')
    
    if response.status_code == 200:
    # Move file to the destination folder
        move_file(file_path, os.path.join(DESTINATION_FOLDER, filename))
        print(f'File moved to {os.path.join(DESTINATION_FOLDER, filename)}')
