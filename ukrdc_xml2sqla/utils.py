from ukrdc_xml2sqla.models.ukrdc import PatientRecord
import ukrdc_sqla.ukrdc as orm
from xsdata.formats.dataclass.parsers import XmlParser


def convert_xml_file(filepath: str) -> orm.PatientRecord:
    """Creates an sqla orm object from a xml file

    Args:
        filepath (str): path to xml file.

    Returns:
        orm.PatientRecord: Patient record orm object.
    """
    with open(filepath, "r") as file:
        data = file.read()

    xsobject = XmlParser().from_string(data)

    return PatientRecord(xsobject).to_orm()
