import hashlib
import copy

from typing import Dict
from lxml import etree  # nosec B410
from xsdata.formats.dataclass.parsers import XmlParser
from ukrdc_xsdata.ukrdc import PatientRecord  # type:ignore
from ukrdc_cupid.core.parse.xml_validate import (
    validate_rda_xml_string,
    SUPPORTED_VERSIONS,
)
from ukrdc_cupid.core.parse.exceptions import SchemaInvalidError
from ukrdc_cupid.core.store.exceptions import SchemaVersionError
from xsdata.formats.dataclass.serializers import XmlSerializer


CURRENT_SCHEMA = max(SUPPORTED_VERSIONS)

serializer = XmlSerializer()


def get_file_metadata(xml_str: str) -> Dict[str, str]:
    """Get file meta data without assuming it conforms to xsdata schema

def get_file_metadata(xml_str: str) -> Dict[str, str]:
    """Get file meta data without assuming it conforms to xsdata schema

    Args:
        xml_str (str): XML file as a string.

    Returns:
        Dict[str, str]: Dictionary of metadata from the file heade.
    """

    xml_doc = etree.fromstring(  # nosec
        xml_str, parser=etree.XMLParser(encoding="utf-8")
    )
    sending_facility = xml_doc.find(".//SendingFacility")
    metadata = {
        "batch_no": sending_facility.get("batchNo"),
        "channel_name": sending_facility.get("channelName"),
        "schema_version": sending_facility.get("schemaVersion"),
        "sending_time": sending_facility.get("time"),
        "sending_extract": xml_doc.find(".//SendingExtract").text,
        "sending_facility": sending_facility.text,
    }

    return metadata


def load_xml_from_str(
    xml_str: str, check_current_schema: bool = False, validate: bool = False
) -> PatientRecord:
    """Utility function to load xml from a string. It applies some checks to
    ensure loading the xml into the xsdata model is possible. However both
    default to False because in a production environment mirth should have
    already flagged if either of these checks fail.

    Args:
        xml_str (str): xml file as a utf-8 string
        check_current_schema (bool, optional): check we are running xsdata compatible schema
        validate (bool, optional): check whether string is valid against that schema

    Raises:
        SchemaVersionError: if the schema version is not supported
        SchemaInvalidError: if the string is not valid against the schema

    Returns:
        PatientRecord: xsdata model of the xml
    """

    if check_current_schema:
        # Check schema version matches the current xsdata version
        metadata = get_file_metadata(xml_str)
        if metadata["schema_version"] < CURRENT_SCHEMA:
            msg = f"XML request on version {metadata['schema_version']} but cupid requires version {CURRENT_SCHEMA}"
            raise SchemaVersionError(msg)

    if validate:
        # Check string is valid against xsdata schema
        errors = validate_rda_xml_string(xml_str)
        if not errors:
            print("file successfully validated")
        else:
            error_table = "\n".join(
                f"Line {line}: {error}" for line, error in errors.items()
            )
            raise SchemaInvalidError(
                f"File failed validation with errors:\n{error_table}"
            )

    return XmlParser().from_string(xml_str, PatientRecord)


def load_xml_from_path(
    filepath: str, validate: bool = True, check_current_schema: bool = True
) -> PatientRecord:
    with open(filepath, "r", encoding="utf-8") as file:
        data = file.read()

    try:
        return load_xml_from_str(
            data, validate=validate, check_current_schema=check_current_schema
        )

    except Exception as e:
        raise Exception(f"Failed to load XML from path {filepath}") from e


def hash_xml(xml: PatientRecord) -> str:
    """
    Take file strip dates etc and produce a hashed version of it
    """
    xml_copy = copy.deepcopy(xml)
    del xml_copy.sending_extract
    xml_reduced = serializer.render(xml_copy)
    xml_hash = hashlib.sha256(xml_reduced.encode("utf-8")).hexdigest()

    return xml_hash[:50]
