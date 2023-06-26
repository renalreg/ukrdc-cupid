"""
Functions to be called in the validation step. 
These will be made available by the api and callable as its own step. This will enable the validity of the xml to be checked prior to any attempt to load and store it (a much more resource heavy process).
TODO: 
    1) generalise to enable the validation of multiple xml versions.
    2) make seperate dependacy group to enable isolated installation of this bit  
"""

import importlib
import pkg_resources
#from schema import ukrdc as rda_schema
from lxml import etree


def validate_rda_xml_string(rda_xml:str):
    """Function to take a RDA xml file and do basic checks against the ukrdc schema

    Args:
        rda_xml (str): xml file as a string 
    """
    
    # Load the XML file
    xml_doc = etree.XML(rda_xml.encode())

    # Load the XSD schema
    xsd_file_path = pkg_resources.resource_filename('schema.ukrdc','UKRDC3.xsd')
    print(xsd_file_path)
    xsd_doc = etree.parse(xsd_file_path)

    #xsd_file_path = pkg_resources.files(module).joinpath('UKRDC.xsd')

    #xsd_doc = etree.parse(str(xsd_file_path))
    xml_schema = etree.XMLSchema(xsd_doc)

    try:
        xml_schema.assertValid(xml_doc)
        # Initially catch errors to allow reporting multiple issues in one file
        return
    
    except etree.DocumentInvalid as e:
        tree = etree.ElementTree(xml_doc.getroot())
        # return errors as dictionary        
        errors = {}
        ## what reason is there for not just returning the error log
        for error in xml_schema.error_log:
            errors[f"line {error.line}"] = error.message
        
        return errors 


