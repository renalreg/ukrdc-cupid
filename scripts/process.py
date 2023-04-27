import glob

from ukrdc_xml2sqla.utils import convert_xml_file

xml_files = glob.glob("xml_examples/*.xml")
for file in xml_files:
    patient_record = convert_xml_file(file)
    if patient_record:
        for item in patient_record.medications.all():
            print(item.fromtime)
