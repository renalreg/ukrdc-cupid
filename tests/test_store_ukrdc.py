""" Unit tests for the classes used for storing the data. The easiest 
way of doing this seems to just be loading a test files with no child objects. 
"""

import ukrdc_xsdata.ukrdc as xsd_ukrdc
from xsdata.formats.dataclass.parsers import XmlParser
from ukrdc_cupid.core.store.models import ukrdc as models
from ukrdc_cupid.core.parse.utils import load_xml_from_path

def test_patient_record_xml_mapping():
    xml = load_xml_from_path(r"scripts/xml_examples/UKRDC.xml")
    #xml = xsd_ukrdc.PatientRecord(XmlParser().from_string(xml_string))
    patient_record = models.PatientRecord(xml)
    patient_record.map_xml_to_tree()

    assert patient_record.orm_object.sendingfacility == "ABC123"
    assert patient_record.orm_object.sendingextract == "UKRDC"


#test_patient_record_xml_mapping()







