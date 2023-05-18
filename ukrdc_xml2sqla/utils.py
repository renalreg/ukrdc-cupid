from xsdata.formats.dataclass.parsers import XmlParser
from xsdata.exceptions import ParserError
from sqlalchemy.orm import Session
from sqlalchemy import Sequence


def load_xml_from_path(filepath: str):
    with open(filepath, "r") as file:
        data = file.read()

    try:
        xsobject = XmlParser().from_string(data)
        return xsobject

    except ParserError as e:
        # print(f"xml file {filepath} failed to parse due to exception: {e}")
        return e


def mint_new_pid(session: Session):
    """
    Function to mint new pid. This sequence doesn't currently exist in the ukrdc, create by running script make_pid_generation_sequence.py
    """
    new_pid_seq = Sequence("generate_new_pid")
    new_pid = str(session.execute(new_pid_seq))

    return new_pid
