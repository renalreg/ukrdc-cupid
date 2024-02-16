""" Script to drive the bits of functionality which will end up in the new 
JTrace replacement. The aim here is not to handle any of the merging. Simply 
to load an xml file into a sqla object with all the correct keys.     
"""

import glob
import os

from xsdata.exceptions import ParserError
from ukrdc_cupid.core.utils import DatabaseConnection
from ukrdc_cupid.core.parse.utils import load_xml_from_path
from ukrdc_cupid.core.general import process_file
from ukrdc_cupid.core.parse.xml_validate import validate_rda_xml_string

#session = DatabaseConnection(env_prefix="UKRDC").create_session(clean=True, populate_tables=True
ukrdc_session = DatabaseConnection(env_prefix="UKRDC").create_session(True, True)
investigate_session = DatabaseConnection(env_prefix="INVESTIGATE").create_session(True, True)

# Specify the directory where your XML files are located
xml_directory = ".xml_to_load/converted"

# grab files to load from directory
xml_files = glob.glob(os.path.join(xml_directory, "*.xml"))

with ukrdc_session() as ukrdc:
    with investigate_session() as investigate:
        for xml_file in xml_files:
            # load file and validate it 
            xml_object = load_xml_from_path(xml_file)
            schema_version = xml_object.sending_facility.schema_version

            investigation = process_file(
                xml_object, 
                ukrdc_session=ukrdc, 
                investigations_session=investigate
            )

            if investigation:
                # we add the file to the investigation it has been created
                investigation.append_file(
                    xml = str(xml_object),
                    filename = xml_file
                )