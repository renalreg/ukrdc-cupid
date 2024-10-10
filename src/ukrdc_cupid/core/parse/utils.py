import hashlib
import copy

from xsdata.formats.dataclass.parsers import XmlParser
from ukrdc_xsdata.ukrdc import PatientRecord  # type:ignore
from ukrdc_cupid.core.parse.xml_validate import validate_rda_xml_string
from xsdata.formats.dataclass.serializers import XmlSerializer

serializer = XmlSerializer()


def load_xml_from_str(xml_str: str):
    xsobject = XmlParser().from_string(xml_str, PatientRecord)  # type:ignore
    schema_version = xsobject.sending_facility.schema_version
    return xsobject, schema_version


def load_xml_from_path(filepath: str) -> PatientRecord:
    with open(filepath, "r", encoding="utf-8") as file:
        data = file.read()

    xsobject = XmlParser().from_string(data, PatientRecord)  # type:ignore
    schema_version = xsobject.sending_facility.schema_version
    xml, schema_version = load_xml_from_str(data)
    errors = validate_rda_xml_string(data, schema_version)
    if not errors:
        print(f"file {filepath} successfully validated")
    else:
        print(errors)

    # We validate file before returning

    return xml


def hash_xml(xml: PatientRecord):
    """
    Take file strip dates etc and produce a hashed version of it
    """
    xml_copy = copy.deepcopy(xml)
    delattr(xml_copy, "sending_extract")
    xml_reduced = serializer.render(xml)
    xml_hash = hashlib.sha256(xml_reduced.encode("utf-8")).hexdigest()

    return xml_hash[:50]
