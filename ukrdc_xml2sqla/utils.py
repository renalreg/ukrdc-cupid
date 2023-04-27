from xsdata.exceptions import ParserError
from ukrdc_xml2sqla.models.ukrdc import PatientRecord
import ukrdc_sqla.ukrdc as orm
from xsdata.formats.dataclass.parsers import XmlParser

def load_from_path(filepath:str)->str:
    with open(filepath, "r") as file:
        data = file.read()
    return data
    

def convert_xml_file(filepath: str) -> orm.PatientRecord:
    """Creates an sqla orm object from a xml file

    Args:
        filepath (str): path to xml file.

    Returns:
        orm.PatientRecord: Patient record orm object.
    """

    data = load_from_path(filepath)
    try:
        xsobject = XmlParser().from_string(data)
        return PatientRecord(xsobject).to_orm()

    except ParserError as e:
        print(f"xml file {filepath} failed to parse due to exception: {e}")


