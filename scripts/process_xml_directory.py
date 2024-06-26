""" Script to drive the bits of functionality which will end up in the new 
JTrace replacement. The aim here is not to handle any of the merging. Simply 
to load an xml file into a sqla object with all the correct keys.     
"""

import glob
import os

from ukrdc_cupid.core.utils import DatabaseConnection
from ukrdc_cupid.core.parse.utils import load_xml_from_path
from ukrdc_cupid.core.general import process_file
from ukrdc_cupid.core.parse.xml_validate import validate_rda_xml_string

ukrdc_sessionmaker = DatabaseConnection(env_prefix="UKRDC").create_sessionmaker()

# Specify the directory where your XML files are located
xml_directory = ".xml_to_load"

# grab files to load from directory
xml_files = glob.glob(os.path.join(xml_directory, "*.xml"))

with ukrdc_sessionmaker() as ukrdc_session:
    # with investigate_session() as investigate:
    for xml_file in xml_files:
        # load file and validate it
        xml_object = load_xml_from_path(xml_file)
        schema_version = xml_object.sending_facility.schema_version

        # validate_rda_xml_string(xml_object)

        investigation = process_file(
            xml_object,
            ukrdc_session=ukrdc_session,
        )

        if investigation:
            # we add the file to the investigation it has been created
            investigation.append_file(xml=str(xml_object), filename=xml_file)
