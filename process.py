import glob

from ukrdc_xml2sqla.models.ukrdc import PatientRecord
from xsdata.formats.dataclass.parsers import XmlParser
import ukrdc_xsdata.ukrdc as xsd_ukrdc

xml_files = glob.glob("xml_examples/*.xml")
print(xml_files)
for file in xml_files:
    with open(file, 'r') as file:
        data = file.read()

    #print(data)
    xsobject = XmlParser().from_string(data)


    patient_record = PatientRecord(xsobject).to_orm()
    print(patient_record)