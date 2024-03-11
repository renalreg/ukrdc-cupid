from xsdata.formats.dataclass.parsers import XmlParser
from ukrdc_xsdata.ukrdc import PatientRecord  # type:ignore
from ukrdc_cupid.core.parse.xml_validate import validate_rda_xml_string


def load_xml_from_path(filepath: str) -> PatientRecord:
    with open(filepath, "r") as file:
        data = file.read()

    xsobject = XmlParser().from_string(data, PatientRecord)  # type:ignore
    schema_version = xsobject.sending_facility.schema_version
    errors = validate_rda_xml_string(data, schema_version)
    if not errors:
        print(f"file {filepath} successfully validated")
    else:
        print(errors)

    # We validate file before returning

    return xsobject
