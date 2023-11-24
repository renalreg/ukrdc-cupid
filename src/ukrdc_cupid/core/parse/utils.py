from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.exceptions import ParserError
from ukrdc_xsdata.ukrdc import PatientRecord


def load_xml_from_path(filepath: str):
    with open(filepath, "r") as file:
        data = file.read()

    try:
        xsobject = XmlParser().from_string(data, PatientRecord)  # type:ignore
        return xsobject

    except ParserError as e:
        # print(f"xml file {filepath} failed to parse due to exception: {e}")
        return e
