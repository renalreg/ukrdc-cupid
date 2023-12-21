from xsdata.formats.dataclass.parsers import XmlParser
from ukrdc_xsdata.ukrdc import PatientRecord  # type:ignore


def load_xml_from_path(filepath: str) -> PatientRecord:
    with open(filepath, "r") as file:
        data = file.read()

    xsobject = XmlParser().from_string(data, PatientRecord)  # type:ignore
    return xsobject
